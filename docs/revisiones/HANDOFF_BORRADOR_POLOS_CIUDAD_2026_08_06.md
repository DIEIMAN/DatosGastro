# HANDOFF · Parejidad de cobertura y primera poligonización de toda la Ciudad · 2026-08-06

Continúa `HANDOFF_BASE_GASTRONOMICA_2026_08_06.md`, vigente en todo lo que no se contradiga acá.
Rama `mercados-gastronomicos-v2`. **Sin commit. Google Places: 0 requests. El total de agosto
sigue en 306.** Ninguna cifra publicada se tocó; el Atlas no se tocó.

La etapa de juntar fuentes queda cerrada. Lo que sigue está corrido.

---

## Lo que cambió, en una línea

**La cobertura de la base es pareja entre barrios, y el borrador de polos de toda la Ciudad ya
existe: 118 polos con un solo juego de parámetros, que encuentran 15 de las 22 zonas publicadas y
agregan 68 que el Atlas no tiene.** Y el borrador trajo dos límites que no se veían antes.

---

## 1 · Los dos indicadores de parejidad · `PAREJIDAD_COBERTURA.txt`

Script nuevo: `scripts/barrido_ciudad/parejidad_cobertura.py`. Bajador:
`scripts/barrido_ciudad/bajar_censo_2022.py` (INDEC, CC BY 4.0). 0 requests a Places.

### La razón pedida no se puede leer sola, y su descomposición sí

`locales ÷ parcelas comerciales` mezcla dos cosas y por eso se reporta partida:

```
base ÷ comercial  =  (base ÷ gastronómicas del Relevamiento)  ×  (gastronómicas ÷ comercial)
   475,8 por mil  =              2,55 cobertura               ×      186,8 por mil composición
```

El segundo factor **no es un defecto de la base: es el territorio**. Palermo tiene más gastronomía
por comercio que Villa Riachuelo y eso no es sesgo de medición. El factor que habla de la base es
el primero.

### El resultado: la cobertura es pareja, y el sur no se desploma

| medida | mediana | CV | p90/p10 | banda escrita antes |
|---|---:|---:|---:|---|
| razón pedida (base/comercial) | 387,7 | 1,37 | 2,76 | — no falsable |
| composición (Relevamiento/comercial) | 158,2 | 0,54 | 2,55 | — es el territorio |
| **cobertura (base/Relevamiento)** | **2,46** | **0,30** | **1,21** | CV < 0,25 y p90/p10 < 2 |

**Veredicto partido, y se informa partido:** el `p90/p10` de 1,21 entra holgado en la banda —el 80 %
central de los barrios está entre 2,30 y 2,78—, y el CV de 0,30 queda afuera. Lo que rompe el CV
son dos barrios chicos: Puerto Madero (7,45, con 52 parcelas comerciales relevadas) y Versalles
(4,16, con 25 gastronómicas). Sacando el 5 % de cada cola el CV baja a **0,07** con 42 barrios entre
2,29 y 2,90 — pero **ese recorte no estaba declarado y va rotulado como diagnóstico, no como
veredicto que reemplace a la banda.**

Y la pregunta que motivaba todo:

```
sur (comunas 4, 8, 9), 10 barrios : cobertura 2,50 | composición 129,1 por mil
resto,                 38 barrios : cobertura 2,45 | composición 163,3 por mil
```

**El sur no está peor cubierto. Tiene menos gastronomía**, medida caminando por un tercero. La
diferencia que se veía en los conteos es composición, no cobertura.

Dos controles más pasan: la cobertura no se ordena por año del relevamiento rotativo (2022: 2,42 ·
2023: 2,40 · 2024: 2,56), y las dos atribuciones de barrio —la del Relevamiento por parcela y la
geométrica de la base— difieren en **2 locales sobre 10.888**.

### Por qué el Relevamiento sirve de vara, y qué le falta

El Relevamiento de Usos del Suelo trae `TIPO1` de las **318.607 parcelas** de la Ciudad, no sólo las
gastronómicas: 58.272 son `UNICOMERCIAL` activas, y ahí adentro cae el 100 % de lo gastronómico. Es
lo más parecido a una medición homogénea del territorio que hay en el proyecto: caminó los 48
barrios, parcela por parcela.

**Su límite, declarado:** el Relevamiento **está adentro de la base** (aporta 10.890 de sus 42.342
registros), así que `base ÷ Relevamiento` no puede bajar de 1 y lo que mide es cuánto agregan las
otras seis fuentes sobre ese piso. Se reporta también sin el piso (`aporte_otras_fuentes`, mediana
1,46), y la conclusión no cambia.

### Indicador B · locales cada mil habitantes · Censo 2022

Población en viviendas particulares, **3.095.454**, verificada contra dos archivos distintos del
INDEC que dan exactamente lo mismo (el `POB_TOT_P` del shapefile de radios y la tabla de personas
por radio). El rótulo dice «en viviendas particulares» y no «población de la Ciudad»: la
diferencia con el total publicado es la población en viviendas colectivas.

```
CABA: 8,96 locales cada mil habitantes
comuna 1 : 19,00      comuna 8 : 2,91
San Nicolás: 38,84    Villa Lugano: 2,27
```

**Se esperaba dispersión alta y se obtuvo dispersión alta, y eso NO es un diagnóstico de
cobertura.** La gastronomía se ubica donde hay oficinas y turismo, no donde hay camas. El indicador
sirve para presentar y para ver el caso extremo; para cobertura sirve el A.

Población por barrio: repartida por área desde los 3.820 radios censales. **El 20,5 % de la
población vive en radios que tocan más de un barrio**, así que la comuna —que es el departamento
censal y no necesita reparto— es la unidad de referencia y el barrio la lectura auxiliar.

---

## 2 · El borrador de polos de toda la Ciudad · `outputs/BARRIDO_CIUDAD_2026-08/borrador_polos/`

Script: `scripts/barrido_ciudad/borrador_polos_ciudad.py`. Mapas:
`scripts/barrido_ciudad/mapa_borrador_polos.py`. **BORRADOR: no se publica, no se sella, no toca el
Atlas.** Rotulado adentro de las dos imágenes, no sólo en el nombre de la carpeta.

### Los parámetros, únicos y anclados afuera de estos datos

```
min_cluster_size = 40   la zona más chica que el Atlas ya publicó tiene 40 establecimientos
                        (R16 Donado–Holmberg y R20 García del Río). Ancla editorial vieja.
min_samples      = 10   cuántos vecinos hacen denso a un punto
método           = eom  el algoritmo elige la profundidad; no se impone cantidad de polos
concave_hull     = 0,55 el ratio ya adoptado por config_territorial_v3.json
universo         = anillo núcleo, sólo apto_geometria = True (23.981 de 27.727 locales)
```

Ningún parámetro se movió por barrio. La grilla de sensibilidad completa (5 × 3) se corrió y se
publica: entre las 13 corridas que separan polos, el número va de **51 a 323**, y el adoptado da
118. El mapa cambia de resolución con el umbral; no cambia de naturaleza.

### El resultado

| | |
|---|---:|
| polos | **118** |
| locales agrupados | 13.564 (56,6 %) |
| **locales fuera de todo polo** | **10.417 (43,4 %)** |
| superficie de los polos | 3.745 ha (18,4 % de la Ciudad) |
| tamaño: mín / mediana / máx | 40 / 66 / 1.314 locales |
| barrios con al menos un polo | 42 de 48 |
| **control §5: envolventes que pasan** | **118 de 118** (mínimo 93,9 % de aptos adentro) |

**El 43 % de la gastronomía de la Ciudad no está en ningún polo.** No es un defecto del método: es
el dato. La mayor parte de la oferta es dispersa, y eso condiciona cualquier política que se
piense sólo en clave de polos.

### El borrador como diagnóstico del §10, que era el otro encargo

Contraste contra el Relevamiento, que no depende de dónde miraron nuestras fuentes:

- **Correlación de Spearman entre gastronomía relevada a pie y locales en polos, por barrio: 0,83.**
- Los 6 barrios sin ningún polo (Paternal, Villa Real, Parque Chas, Coghlan, Agronomía, Versalles)
  suman **287 parcelas gastronómicas relevadas, el 2,6 % de la Ciudad**, con composición mediana de
  138 por mil contra 158 de la Ciudad.
- **Barrios con gastronomía relevada por encima de la mediana y sin polo: 0.**

No aparecen polos donde miramos más. Aparecen donde el Relevamiento encontró gastronomía.

---

## 3 · Los dos límites que trajo el borrador, y son lo más importante que salió hoy

### 3.1 · Un solo juego de parámetros NO es un solo umbral de densidad

HDBSCAN es adaptativo por diseño: fija cuántos vecinos hacen denso a un punto y deja que la
distancia la ponga el territorio. Correr los 48 barrios con el mismo parámetro impone **la misma
regla**, y la regla da **un umbral distinto en cada lugar**.

| tercio | polos | ha por polo | densidad (locales/ha) |
|---|---:|---:|---|
| menos denso | 40 | 62,6 | 1,0 – 3,9 |
| medio | 39 | 19,9 | 3,9 – 6,7 |
| más denso | 39 | 11,9 | 6,7 – 15,2 |

El polo más denso tiene **16 veces** la densidad del menos denso. En la periferia el método dibuja
manchas grandes y flojas; en el centro, piezas chicas y apretadas. **Un polo de Lugano y uno de San
Nicolás llevan la misma etiqueta y no son la misma cosa.**

Es una decisión pendiente y es de Diego: o se acepta la vara relativa —cada zona contra su
entorno— o se pasa a un piso absoluto en locales por hectárea, que es otra corrida y otra
discusión. Diez polos ya están marcados como grandes y poco densos, candidatos a partir o
descartar; el mayor es **P072, 1.314 locales sobre 440,7 ha a 3,0 locales/ha**, que encadena
Belgrano, Núñez y Colegiales en una sola mancha que ningún peatón reconocería como un polo.

### 3.2 · La ablación por fuente, con estos parámetros, casi no es interpretable

Se corrió la ablación (sacar un grupo de independencia por vez) **con control aleatorio**: cinco
sorteos sacando al azar la misma cantidad de puntos. Sin ese control la tabla se leía al revés.

| grupo quitado | −% puntos | polos | colapsa | azar colapsa | lectura |
|---|---:|---:|---|---|---|
| GCBA_URBANISMO (Relevamiento) | 37,5 | 5 | **sí** | 0/5 | **la fuente sostiene el mapa** |
| OVERTURE_FSQ_ATP | 36,6 | 64 | no | 0/5 | interpretable: sobrevive el 71 % |
| GCBA_AGC (F01+F02) | 21,5 | 82 | no | 2/5 | sus puntos son redundantes |
| OSM | 23,5 | 5 | sí | 1/5 | **no interpretable** |
| GCBA_ESPACIO_PUBLICO | 0,0 | 118 | no | 0/5 | no aporta ningún local propio |

El hallazgo que sí queda firme: **el Relevamiento de Usos del Suelo sostiene el mapa.** Sin él la
corrida se rompe, y sacar la misma cantidad de puntos al azar no la rompe ninguna de las cinco
veces. La base de polos de la Ciudad descansa hoy sobre esa fuente.

Y el límite del diseño de la prueba: **el umbral de colapso cae adentro del rango de tamaños que la
ablación necesita probar.** Con parámetros calibrados a la densidad actual, no se puede separar
limpiamente «la fuente sostenía el polo» de «faltaron puntos». Hay que arreglar la prueba antes de
usarla para decidir nada.

### 3.3 · El anillo núcleo no es una elección cosmética

Con panaderías y pastelerías adentro, **el 99,6 % de los puntos cae en un solo cluster**: la Ciudad
deja de tener polos separables con estos parámetros. No es un mapa alternativo, es una corrida que
no se puede hacer así.

---

## 4 · El cotejo contra las 22 zonas publicadas

Umbrales escritos antes de correr: zona **encontrada** si el borrador le cubre ≥ 25 %; polo **nuevo**
si menos del 25 % de su superficie ya estaba publicada.

```
zonas publicadas que el borrador ENCUENTRA :  15 de 22
zonas publicadas que NO encuentra          :   7
polos del borrador NUEVOS                  :  68 de 118
superficie: publicada 3.842 ha | borrador 3.743 ha | compartida 1.225 ha
```

### Las que coinciden

R05 Belgrano (99,2 % cubierta), R01 Palermo (63,0), R02 Corrientes (61,1), R13 Abasto (55,4),
R10 Caballito (41,7), R09 Chacarita (41,5), R18 Esmeralda–Paraguay (40,5), R15 Devoto (39,3),
R19 Federico Lacroze (38,9), R12 Centro/Microcentro (38,3), R14 Boedo (38,1), R06 Recoleta (37,1),
R08 Villa Crespo (32,3), R17 Villa Urquiza (29,1), R03 San Telmo (25,8).

### Las siete que el clustering NO encuentra, que es la lista interesante

| ref | zona | ha | cubierta |
|---|---|---:|---:|
| R20 | García del Río | 28,4 | 24,7 % |
| R07 | Costanera Norte | 38,5 | 16,1 % |
| R16 | Donado–Holmberg | 119,0 | 14,9 % |
| R21 | La Paternal | 321,0 | 13,2 % |
| **R04** | **Puerto Madero** | **314,5** | **9,3 %** |
| R22 | Villa Pueyrredón | 305,6 | 9,3 % |
| R11 | Boulevard Caseros | 50,0 | 5,5 % |

Cuatro de las siete son zonas grandes con poca gastronomía adentro (R21, R22, R04, R16): el
perímetro publicado es mucho más ancho que la concentración. R20 quedó a 0,3 puntos del umbral.
**R04 Puerto Madero es el caso a mirar**: 314 ha publicadas, 9,3 % cubierto, y su Relevamiento
declara sólo 52 parcelas comerciales activas en todo el barrio, un número implausible que hace
sospechar del Relevamiento ahí antes que de la base.

### Y el hallazgo más grande del cotejo, que no depende de ningún umbral

**Las comunas 8 y 9 no tienen NINGUNA zona publicada del Atlas, y el borrador encuentra 10 polos
con 1.000 locales ahí**, con los mismos parámetros que usó en Palermo. Se ve de un vistazo en
`borrador_vs_22_zonas.png`: todo el sur y el sudoeste está lleno de verde y no tiene un solo
contorno rojo.

Los polos nuevos más grandes: P103 San Telmo (342 locales, corrido respecto de R03), P021 Liniers
(262), P073 Palermo (207), P048 Colegiales (171), P025 Monte Castro (162), P076 Recoleta (156),
P037 Villa del Parque (142), P004 Villa Lugano (141).

Un caso que los dos umbrales por separado no veían y ahora sale marcado: **P072 contiene entera a
R05 Belgrano y aun así solapa sólo el 12,8 %**, porque es once veces más grande. No es un polo
nuevo: es la misma zona con otro perímetro.

---

## Lo que espera decisión

1. **La vara de densidad (§3.1).** Vara relativa como está, o piso absoluto en locales por
   hectárea. Condiciona todo lo que siga.
2. **Qué hacer con los 10 polos grandes y poco densos**, empezando por P072.
3. **Places sigue en pausa**, sin criterio de destino. El borrador no cambió eso: no hay ninguna
   zona con faltante demostrado.
4. **Puerto Madero:** verificar el Relevamiento antes de concluir nada sobre R04.
5. Siguen abiertos de ayer: la cláusula ODbL de OSM en legal, el visto de Patricia sobre el
   pasaje 5, la lista de Bares Notables contra la normativa, Foursquare, y la nota a la AGC.

## Lo que no se tocó

Ninguna cifra publicada. Ningún PDF. Los JSON congelados de las dos ediciones. El pipeline público
F01–F05. `PROTECTED_SURFACES.yaml`. Las 22 envolventes editoriales (se leyeron, no se escribieron).
La base (`local.csv` no se regeneró). **Google Places: 0 requests.**

## Trampas encontradas hoy

- **Un número de clusters siempre parece una respuesta.** Con `min_samples` alto HDBSCAN devuelve
  «5 polos» que son la Ciudad entera en una mancha, y la fila se lee como una corrida más
  conservadora. Sin un umbral de colapso declarado, dos filas de la sensibilidad y dos de la
  ablación se habrían leído al revés.
- **Una ablación sin control aleatorio mide densidad, no fuentes.** Sacar una fuente saca puntos, y
  los parámetros están calibrados a la densidad actual. Tres de las cinco filas cambiaron de
  significado al agregar el control.
- **«Mismos parámetros» no es «misma vara».** Un método adaptativo con un solo juego de parámetros
  aplica un umbral distinto en cada barrio, que es casi lo contrario de lo que la regla quería
  evitar. La regla se cumplió al pie de la letra y no consiguió lo que buscaba.
- **Dos umbrales de solape, uno por sentido, dejan un caso ciego en el medio.** El polo que contiene
  entera a una zona chica sale «nuevo» y la zona sale «encontrada»: las dos cosas a la vez y
  ninguna correcta. Hizo falta una tercera columna.
- **Un cociente que mezcla cobertura y composición no se puede leer, y parece que sí.** La
  descomposición no era un lujo: sin ella, «el sur da más bajo» se habría leído como falta de
  cobertura cuando es menos gastronomía.
