# Las seis vías, el índice de corredor y el control de las 22 · 2026-08-07

Corrida sobre la definición que Diego fijó el 2026-08-07 (`QUE_ES_UN_POLO.md`).
**Google Places: 0 requests.** Ninguna geometría publicada tocada. Ninguna cifra del Atlas tocada.
La lectura de las tres corridas estaba escrita antes de correr, en `LECTURA_PREVIA.md`.

Scripts nuevos: `polos_soporte.py`, `polos_indice_corredor.py`, `polos_seis_vias.py`,
`polos_matriz_seis_vias.py`, `hitos_cerrar_bares_notables.py`.

---

## 0 · La relectura del control de ayer, escrita como corresponde

El control de la Tarea 4 de ayer midió **una vía de seis**. Su resultado, redactado con la
definición nueva, es:

> **El relevamiento confirma por la vía de densidad.** De los 20 candidatos `incluir_*`, 16
> aparecen como concentración medida. De los 5 `no_incluir_aun`, ninguno. Lo que no se probó —y no
> se podía probar con esa sonda— es si alguno entra por trayectoria, mercados, comunidades,
> reconocimiento o forma.

Y hay un caso que obliga a agregar algo más, porque el propio enunciado se apoya en él:

### Av. Boedo no tenía «cero señal de concentración». La sonda no la veía.

| sonda | qué mide | resultado |
|---|---|---|
| calle (ayer) | locales con dirección sobre la calle Boedo | **17 locales, 0 polos** |
| envolvente publicada R14 (hoy) | locales dentro de la envolvente editorial del Atlas | **245 locales, 2 polos** (P029, P062) |

Boedo abre **tres** vías medibles: **A** (densidad), **B** (Café Margot y Esquina Homero Manzi
adentro) y **F** (elongación 4,08 · corredor). El caso sigue probando lo que Diego quería que
probara —que el descarte por «no encontré una nota de diario» estaba mal— pero **no por falta de
concentración: por una sonda que medía el frente de la avenida y no la zona.** Es la misma
familia de error que tumbó a R18, R19 y R21 como candidatas de Places.

---

## 1 · TAREA 2 · El índice de corredor · **RAMA B**

### El índice

Sobre la nube de puntos del soporte, en EPSG:5347: `elongacion = σ1/σ2` del PCA. Largo sobre
ancho, adimensional. Acompañan `frac_banda_100m`, `ancho_p80_m`, `largo_p5_p95_m` y la elongación
del **rectángulo rotado mínimo del polígono**, que mide la forma dibujada y no la de los puntos.

Corte declarado antes de correr: **2,0** — convención geométrica, no un corte leído del histograma.

### La calibración contra las 22, con la familia al lado

| | elongación | familia |
|---|---:|---|
| R07 Costanera Norte | 8,06 | multiparte |
| **R19 Federico Lacroze** | **7,14** | eje o corredor |
| **R02 Avenida Corrientes** | **4,27** | eje o corredor |
| **R14 Avenida Boedo** | **4,08** | eje o corredor |
| R04 Puerto Madero | 3,41 | multiparte |
| **R16 Donado-Holmberg** | **3,38** | eje o corredor |
| **R11 Boulevard Caseros** | **2,95** | eje o corredor |
| R13 Abasto | 2,61 | **Polo** |
| **R20 García del Río** | **2,54** | eje o corredor |
| R15 Devoto | 2,42 | **Polo** |
| … | | |
| R08 Villa Crespo | 1,83 | Polo |
| R05 Belgrano | 1,70 | Polo |
| R06 Recoleta | 1,24 | Polo |
| R03 San Telmo | 1,16 | Polo |

**Las 6 declaradas corredor quedan arriba del corte. Las 6 «Polo» no quedan todas abajo:** Abasto
(2,61) y Devoto (2,42) lo cruzan. Por la lectura escrita antes, eso es **rama B**:

```
AUC(corredor vs Polo) con las 6:  0,972
AUC con las 5 del enunciado:      1,000
```

**El índice se publica con su curva y NO decide solo: acompaña al criterio.** Rama A habría hecho
falta separación perfecta y no la hubo por dos casos. El corte no se movió para conseguirla.

### Dos correcciones al enunciado

**Son seis, no cinco.** `cotejo_22_zonas_final.csv` declara «Eje o corredor» también a **R20
García del Río** —que `QUE_ES_UN_POLO.md` §5 nombra como corredor emergente—. Se calibró con las
seis. Con las cinco del enunciado la separación es perfecta (AUC 1,000); con las seis, 0,972.

**Y la familia «Polo» son seis, no cinco:** R13 Abasto está ahí. La enumeración de la lectura
previa se lo había salteado y quedó corregida en el archivo, con la corrección a la vista.

### La circularidad, medida

```
rho de Spearman entre elongacion (puntos) y elongacion_rect (polígono):  0,949
```

Por encima del 0,80 declarado: **la calibración está contaminada**. Y tiene que estarlo: a lo que
alguien decidió llamar corredor se le dibujó una franja, y los puntos adentro de una franja salen
elongados por construcción. El veredicto de rama B vale, pero lo que valida es que **el índice
lee correctamente la forma que hay**, no que la forma sea un descubrimiento sobre el territorio.

### La salvedad grande: la transferencia de escala

| soporte | n | mediana ha | mediana elongación | ≥ 2,0 |
|---|---:|---:|---:|---:|
| barrio administrativo | 6 | 303,3 | 1,69 | 33 % |
| enclave comunitario | 1 | 17,6 | 1,61 | 0 % |
| envolvente publicada | 20 | 129,8 | 2,12 | 50 % |
| **polo del borrador** | **65** | **12,7** | **2,23** | **63 %** |

El corte se calibró sobre envolventes editoriales de ~130 ha y se aplica sobre polos de ~13 ha.
A esa escala, **la mediana ya está arriba del corte**: 63 % de los polos del borrador dan
«corredor». Un corte que marca a dos tercios de la población no está aislando corredores, está
describiendo lo normal — **a la escala del polo, lo alargado es la regla**, porque un polo chico
se apoya sobre una o dos calles.

Consecuencia práctica: la columna `via_F_forma` es informativa sobre las 22 y sobre las
envolventes, y **no discrimina sobre los polos del borrador**. No se la debe usar ahí para decidir.

### La curva de la banda (R4)

| familia | 50 m | 75 m | 100 m | 150 m | 200 m |
|---|---:|---:|---:|---:|---:|
| Eje o corredor | 0,28 | 0,42 | 0,54 | 0,73 | 0,86 |
| Polo | 0,14 | 0,23 | 0,32 | 0,44 | 0,54 |

La brecha se sostiene a lo largo de todo el rango: la elección de los 100 m **no** es la mitad
del resultado.

---

## 2 · TAREA 1 · Las columnas medibles, sobre las 94 filas

La matriz pasa de **23 a 51 columnas**. Las 23 viejas quedan en el mismo orden y verificadas celda
por celda contra `git HEAD`: **0 diferencias**. Las 28 nuevas van todas al final.

### El soporte, que es la decisión que gobierna todo lo demás

Las 94 filas no son objetos del mismo tipo y la tabla lo dice en una columna, no en una nota:

| soporte | filas | mediana ha |
|---|---:|---:|
| polo del borrador | 65 | 12,7 |
| envolvente publicada | 20 | 129,8 |
| barrio administrativo | 6 | 303,3 |
| enclave comunitario (Barrio Chino) | 1 | 17,6 |
| **sin soporte** | **2** | — |

**`via_A_n_locales` no es la columna `locales` del borrador y no hay que cruzarlas sin mirar.**
Acá se cuentan los puntos que caen **dentro del polígono**; allá se cuentan los **miembros del
cluster**. Sobre las 65 filas comparables la diferencia tiene mediana **−7 locales** (−8,6 % en
promedio): la envolvente cóncava simplificada deja afuera miembros del borde. En un caso va al
revés y por mucho —Palermo Soho, +44—, porque la envolvente de P091 encierra puntos que el cluster
no tomó. Ninguna de las dos está mal; miden cosas distintas y hay que decir cuál se está leyendo.

Bajo Belgrano y Belgrano R siguen **sin soporte**, como las declaró el control de ayer. No se les
inventó uno: darles el polígono de Belgrano entero sería atribuirle a la parte lo del todo.
`n_vias_medibles` en esas dos filas queda **vacío, no cero** — un cero se leería como hallazgo.

### Cuántas filas abre cada vía

| vía | abre |
|---|---:|
| A · densidad y continuidad | 89 de 94 |
| B · trayectoria e instituciones | 40 de 94 |
| C · mercados y centralidades | 4 de 94 |
| D · comunidades | 7 de 94 |
| E · reconocimiento externo | **columna vacía — la llena Diego** |
| F · corredor | 53 de 94 |

Combinaciones más frecuentes: `AF` 30, `ABF` 17, `AB` 16, `A` sola 15.

### Vía B · la desagregación por tipo, con la cobertura al lado y no al pie

| tipo | hitos | con punto | sin punto |
|---|---:|---:|---:|
| Bar Notable (canon del Boletín) | 90 | 90 | 0 |
| MICHELIN | 58 | 57 | 1 |
| Pizzería emblemática | 20 | **0** | **20** |
| Restaurante Icónico | 16 | 16 | 0 |
| 50 Best (ranking internacional) | 16 | 16 | 0 |
| Mercado/patio | 12 | 8 | 4 |
| Heladería histórica | 5 | **0** | **5** |

**Las 20 pizzerías emblemáticas y las 5 heladerías históricas no tienen ni una coordenada.** Vienen
con nombre y barrio, sin altura, y ponerlas en el centroide del barrio sería colocar un hito donde
no está. Un `0` en esas dos columnas de la matriz significa **«no sabemos dónde»**, no «no hay».
Es exactamente el caso de la pizzería San Antonio que Diego cita para Boedo: existe, está
declarada, y no se puede ubicar.

**`via_B_patrimonio_normativo` sale con 2 hitos en toda la Ciudad** —Mercado de San Telmo
(Monumento Histórico Nacional, Decreto 12/2001) y Yiyo el Zeneize (Ley CABA 6.533)—. Estaba
avisado antes de correr y se confirma: **es un hueco de la fuente, no un resultado sobre el
territorio.** La Esquina Homero Manzi, que la definición cita como Sitio Histórico Nacional, en
la capa figura **sólo como Bar Notable**: su declaratoria nacional no está cargada en ningún
archivo del repositorio. Si esa columna va a servir para algo, hay que cargar el patrimonio
declarado; hoy no mide nada.

> Trampa encontrada al construir esa columna: la primera versión buscaba «Ley» en el
> reconocimiento y devolvió **80 hitos**. La distinción de Bar Notable es «Café, Bar, Billar o
> Confitería Notable (**Ley 35**…)», así que los 90 bares entraban por la puerta de atrás y la
> columna dejaba de distinguir nada. Ahora busca el acto **histórico** —monumento, sitio, área de
> protección, patrimonio inmaterial— y da 2.

### Vía C · mercados y patios

Sólo **4 de 94** filas contienen un mercado o patio del listado oficial: Palermo Hollywood
(Bonpland), Caballito (Mercado del Progreso), Costanera Norte (Patio Costanera Norte) y P004 Villa
Lugano (Yiyo el Zeneize). Cuatro de los 8 mercados ubicables **no caen en ninguna de las 94** —de
Belgrano, de San Telmo, Rodrigo Bueno y Patio de los Lecheros—, y eso es cobertura del recorte, no
ausencia del mercado.

Dos cosas que conviene que estén escritas:

- **El Mercado de San Telmo queda 64 m afuera de la envolvente publicada R03.** La zona de San
  Telmo del Atlas no contiene su propio mercado, por 64 metros. Es un dato para la cartografía, no
  para la curaduría.
- **El ex-Mercado de Abasto no está en el listado oficial de mercados y patios**, así que R13
  Abasto **no abre vía C** por esta medición aunque `QUE_ES_UN_POLO.md` lo use como su ejemplo de
  vía C. La vía C se midió contra el listado que existe; si el criterio es más amplio que ese
  listado, hay que decirlo y ampliar la fuente.

### Vía D · los cuatro enclaves, construidos desde el callejero oficial

| enclave | tramos | eje | ha | quién lo toca |
|---|---:|---:|---:|---|
| Barrio Chino | 2 | 385 m | 17,6 | PG006A Barrio Chino |
| Barrio Coreano Baek-ku | 1 | 768 m | 30,1 | PGF2 Flores |
| Pasaje Ruperto Godoy | 1 | 118 m | 10,6 | Flores, Floresta, P052 |
| Microcentro boliviano de Liniers | 3 | 2.828 m | 104,1 | P021, P017, P020 |

Buffer de 150 m. **La curva del buffer** (R4) da 5 filas a 50 m y **7 de 100 m en adelante**, sin
moverse hasta 300 m: el valor elegido cae adentro de la meseta y no está sosteniendo el resultado.

Y una salvedad que hay que leer: **el de Liniers es el único que la delimitación no cierra por los
dos lados.** Dice «José León Suárez **desde** Rivadavia» y después nombra Falcón, Ibarrola y Gral.
Paz sin decir entre qué y qué. Se tomó lo que la delimitación nombra, dentro de Liniers, y salieron
104 ha — cuatro veces el Barrio Chino. Cerrarlo por nuestra cuenta habría sido inventar la
delimitación en vez de leerla; el tamaño queda a la vista para que se lo apriete.

> Trampa: las calles del callejero corren de punta a punta de la Ciudad. José León Suárez mide
> **7,3 km** y cruza cuatro barrios; Av. Gral. Paz rodea la Ciudad entera. La primera versión
> proyectaba el **centroide** de la calle que corta y devolvió un tramo de **10 m** sin fallar. El
> cruce hay que buscarlo como punto más cercano, y el eje hay que acotarlo al lugar que la propia
> delimitación nombra.

### Vía A · la continuidad, y los dos parámetros que no se ponen de acuerdo

Tres medidas, como estaba declarado: `continuidad_60m` (% de locales en la componente conexa mayor
uniendo lo que esté a ≤60 m), `vecino_medio_m` y `vecino_sobre_poisson` (los dos sin parámetro).

**Y el control declarado antes falla en parte:** la correlación de Spearman entre la continuidad a
60 m y la razón observado/Poisson es **0,634**. No dicen lo mismo. El motivo se ve en la tabla: la
continuidad a umbral fijo **depende del tamaño del soporte** —Barrio Chino, 17,6 ha, da 97,3 %;
Flores, 859 ha, da 6,1 %— mientras que la razón de Poisson es adimensional. Entonces:

- para **comparar filas del mismo soporte**, la continuidad a 60 m es legible;
- para **comparar entre soportes**, hay que usar la razón de Poisson, que va de 0,514 a 1,247 con
  mediana 0,779 (todo por debajo de 1 = más agrupado que el azar, como corresponde).

Está publicado con su curva a 20, 40, 60, 80 y 120 m para que la elección se vea.

**La regla de vía A abierta** —algún polo del borrador con ≥50 % de sus locales dentro del
soporte— es estable: 90 filas a 25 %, **89 a 50 %**, 85 a 75 %. Recién a 100 % se cae a 13, que es
lo esperable porque exige que el polo entre entero. El 50 % no es la mitad del resultado.

---

## 3 · TAREA 4 · El control · por cuántas vías entra cada una de las 22

```
  id   zona                              A  B  C  D  F   total
  R05  Belgrano                          X  X  X  X  ·     4
  R07  Costanera Norte                   X  X  X  ·  X     4
  R01  Palermo                           X  X  X  ·  ·     3
  R02  Avenida Corrientes                X  X  ·  ·  X     3
  R04  Puerto Madero                     X  X  ·  ·  X     3
  R10  Caballito                         X  X  X  ·  ·     3
  R13  Abasto                            X  X  ·  ·  X     3
  R14  Avenida Boedo                     X  X  ·  ·  X     3
  R15  Devoto                            X  X  ·  ·  X     3
  R19  Federico Lacroze por tramos       X  X  ·  ·  X     3
  R06  Recoleta                          X  X  ·  ·  ·     2
  R08  Villa Crespo                      X  X  ·  ·  ·     2
  R09  Chacarita                         X  X  ·  ·  ·     2
  R11  Boulevard Caseros                 ·  X  ·  ·  X     2
  R12  Centro / Microcentro segmentado   X  X  ·  ·  ·     2
  R16  Donado-Holmberg                   X  ·  ·  ·  X     2
  R17  Villa Urquiza                     X  X  ·  ·  ·     2
  R18  Esmeralda-Paraguay                X  X  ·  ·  ·     2
  R21  La Paternal                       X  X  ·  ·  ·     2
  R03  San Telmo                         ·  X  ·  ·  ·     1
  R20  García del Río                    ·  ·  ·  ·  X     1
  R22  Villa Pueyrredón                  X  ·  ·  ·  ·     1
```

### La rama que se cumple

**Las 22 abren al menos una vía medible. Ninguna queda en cero.**

> Por la lectura escrita antes: **LA GRILLA SE SOSTIENE SOLA.** No depende del trabajo documental
> para funcionar. La vía E la sigue necesitando para *defender* casos, pero no para *encontrarlos*.

Distribución: 3 zonas con una vía, 9 con dos, 8 con tres, 2 con cuatro.

### Las tres que entran por una sola, y qué dice cada una

- **R03 San Telmo · sólo B.** Vía A cerrada porque su envolvente publicada tiene **71 locales en
  25 ha** y ningún polo del borrador pone ahí la mitad de los suyos: el polo de San Telmo (P103,
  342 locales) desborda largamente la envolvente. No es que San Telmo no tenga concentración; es
  que la envolvente publicada recorta un pedazo chico de la que tiene.
- **R20 García del Río · sólo F.** Coincide exactamente con lo que dice `QUE_ES_UN_POLO.md`:
  entra por F y por E, y E es la columna que llena Diego. Es el caso que demuestra que la grilla
  necesita la columna documental para **defender**, aunque no para encontrar.
- **R22 Villa Pueyrredón · sólo A, y débil.** 198 locales sobre 305 ha con **continuidad 11,6 %**
  —el 8.º valor más bajo de las 92, y los siete de abajo son todos soportes grandes—. La medición
  dice exactamente lo que decía el descarte:
  «dos concentraciones medidas, sin continuidad entre ellas». La vía A abierta y la continuidad
  baja **no se contradicen**: la primera dice que hay concentración, la segunda que no forma
  tejido. Por eso hacían falta las dos columnas y no una.

### El caso más denso de las 94 no es un polo del borrador

**Barrio Chino: 185 locales en 17,6 ha, continuidad 97,3 % a 60 m.** Es la fila con más tejido
continuo de toda la tabla junto a Palermo Soho, y **abre A y D y no abre B**: no hay un solo hito
declarado adentro. Una zona sin ningún reconocimiento patrimonial ni distinción gastronómica, con
el tejido más continuo que mide el instrumento. Es el mejor argumento a favor de que la grilla
tenga seis vías y no una.

---

## 4 · TAREA 3 · Los tres cierres

### a) Los homónimos · el número no da 74, da **71**, y estaba avisado antes de correr

Las cuatro líneas impresas son **tres bares**: Café Palacio salía dos veces porque la entidad ya
fusionada tenía dos nombres.

| bar | juntaba | queda en |
|---|---|---|
| **Café Palacio** | (GCBA + Boletín) + Wikidata | **las tres** |
| Bar Bidou | Wikidata + Boletín | dos |
| El Preferido de Palermo | GCBA + Wikidata | dos |

```
bares distintos      114  →  111
en las TRES listas    70  →   71     (el enunciado predecía 74)
```

Sólo Café Palacio suma a «en las tres»; los otros dos juntan dos listas cada uno. El número manda.

**Y las fusiones dejan tres equivalencias de calles, que son dato para el normalizador:**

```
«BORGES JORGE LUIS»  =  «BORGES JORGE L»      residuo de iniciales, ya declarado abierto
«FEDERICO LACROZE»   =  «F LACROZE»           residuo de iniciales, ya declarado abierto
«DIAGONAL NORTE»     =  «PENA ROQUE SAENZ»    NO es residuo: dos nombres oficiales de la misma
                                              calle. Ninguna regla de tokens la cierra. Es tabla.
```

### b) Manda el Boletín Oficial

**Canon: 90 bares, los 90 con coordenada** —71 heredadas del catálogo del GCBA, 19 geocodificadas
con USIG, 0 sin resolver, 0 requests pagos—. Es la capa de Bar Notable que usa la vía B.

Fuera del canon quedan **21**, anotados y no descartados:

- **8 sólo en Wikidata** (eran 11; tres se fueron en las fusiones): American Bar, Bar Carlitos,
  Café Retiro, Café de los Incas, Confitería Queen Bess, Confitería Richmond, Confitería del Hotel
  Castelar, Victoria.
- **5 sólo en GCBA** — el enunciado no los nombra y también quedan fuera: el catálogo del GCBA es
  oficial pero no es la declaratoria. Bar Lavalle, Bidou de las Luces, Café Victoria, Confitería
  del Hotel Castelar (Av. de Mayo 1048), Olimpo.
- **8 en GCBA *y* Wikidata que el Boletín no tiene**, y son los que más merecen que alguien mire el
  acto administrativo: Café Nostalgia, Café Los Andes, Café Monserrat, Café de la Esquina, El
  Preferido de Palermo, Iberia, La Embajada, La Nueva Andaluza.

La capa vigente se escribió **aparte**: `hitos_capa_unificada.csv` queda intacto para poder
comparar contra el estado de ayer.

### c) La matriz bajo control de versiones

Ya estaba versionada desde `aea2cdc`. Las 28 columnas nuevas entran versionadas con ella.

---

## Trampas encontradas hoy

- **Un filtro que no matchea nada devuelve un veredicto perfecto.** La primera pasada del índice
  leyó la columna `familia` del geojson —que trae la etiqueta corta, «eje», «polo»— comparándola
  contra la larga. Las dos familias quedaron **vacías**, y la condición de la rama A —«todos los
  corredores arriba y todos los polos abajo»— **se cumple trivialmente sobre conjuntos vacíos**.
  La corrida terminó sin error y declaró rama A. Ahora corta si una familia queda vacía.
- **Un merge que colisiona se queda con la columna vieja.** Al volver a correr la incorporación a
  la matriz, `n_vias_medibles` existía en los dos lados: pandas dejó la vieja con su nombre y la
  nueva con sufijo, la asignación tomó la vieja, y el reporte anunció que había escrito la nueva.
  Se arregla borrando las columnas de destino antes de unir.
- **El centroide de una calle no es dónde cruza.** Av. Gral. Paz rodea la Ciudad; su centroide no
  está ni cerca de donde toca a José León Suárez. Proyectarlo devolvió un tramo de 10 m.
- **Un patrón demasiado ancho vacía de sentido una columna.** Buscar «Ley» para detectar patrimonio
  normativo trajo los 90 bares notables, porque su propia distinción es una ley.
- **Una sonda mal elegida produce un «cero» que se lee como territorio.** Boedo no tenía cero
  concentración: la sonda de calle veía 17 locales donde la envolvente ve 245.

---

## Lo que espera decisión de Diego

1. **La vía E.** La columna está creada y vacía en las 94 filas. Es la única que falta para que la
   grilla esté completa.
2. **`via_F_forma` sobre los polos del borrador.** El 63 % da «corredor». O se acepta que a esa
   escala la forma no discrimina, o se calibra un corte propio para esa escala —que sería un corte
   nuevo y tendría que anclarse afuera, no en la distribución de los polos.
3. **El patrimonio normativo.** Dos hitos en toda la Ciudad. Si la vía B tiene que contarlo, hay
   que cargar la fuente: Homero Manzi como Sitio Histórico Nacional no está en ningún archivo.
4. **Las 20 pizzerías y las 5 heladerías sin coordenada.** Hoy son ceros que parecen ausencias.
5. **El recorte del enclave de Liniers**, que la delimitación no cierra: 104 ha es lo que sale de
   leerla literal.
6. **El listado de mercados de la vía C**, si el criterio incluye centralidades como el ex-Mercado
   de Abasto que el listado oficial no tiene.
7. **La envolvente R03 de San Telmo**, que deja su propio mercado 64 m afuera.
8. Sigue de antes: las 39 filas nuevas que superponen territorio de una fila vieja, `Ultramarinos`
   sin geocodificar, y el resto del pendiente del handoff del 2026-08-06.
