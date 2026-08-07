# LECTURA PREVIA · las seis vías, el índice de corredor y el control de las 22

**Escrito antes de correr nada.** Es el requisito R1 del método: qué resultado significaría qué,
con las bandas y los cortes fijados de antemano. Lo que sigue no se toca después de ver los
números. Si un corte queda incómodo, se reporta incómodo.

Fecha: 2026-08-07 · rama `mercados-gastronomicos-v2` · Google Places: **0 requests**.

---

## 0 · Lo que ya está decidido y no se re-discute

De `QUE_ES_UN_POLO.md` (Diego, 2026-08-07):

- **No hay umbral de cantidad.** Ningún número decide si algo es polo.
- **No se agrupa por barrio.** La delimitación responde a evidencia territorial, no a límites
  administrativos.
- **No hay escala única.** Núcleo compacto, corredor, sucesión de centralidades y sistema de
  subpolos son morfologías legítimas.
- Un candidato entra **por una sola vía**. Cumplir varias no lo hace más polo.

Y la relectura del control de ayer: midió **una** de seis vías. Su resultado se reescribe como
**«el relevamiento confirma por la vía de densidad»**, no como «confirma, no descubre».

---

## 1 · El universo de puntos, fijado una vez para las tres corridas

Todo lo que se mida sobre puntos usa **el mismo universo con el que se construyeron los 124
polos del borrador**, para que las cifras sean comparables entre filas:

```
base            outputs/BARRIDO_CIUDAD_2026-08/base/local.csv
filtro          anillo == "nucleo"  AND  apto_geometria == True
CRS             EPSG:5347 (métrico de la Ciudad; en grados las áreas y las distancias salen mal)
```

Usar la base completa daría números más grandes y **no comparables** con `borrador_polos_v3.csv`.
Se declara acá y no se cambia.

---

## 2 · El soporte geométrico de cada fila · declarado antes, con su procedencia

Las 94 filas de la matriz **no son objetos del mismo tipo** y no se puede fingir que sí. Cada una
recibe un soporte, y el soporte viaja en la tabla como columna, no como nota al pie:

| grupo | filas | soporte | procedencia |
|---|---:|---|---|
| `PGR_*` | 62 | polígono del polo en `borrador_polos_v3.geojson` | algorítmica (HDBSCAN + envolvente cóncava) |
| Palermo Soho / Hollywood / Cañitas | 3 | polos P091 / P078 / P065 | resolución declarada en `DONDE_ESTA_SOHO.txt` |
| Barrio Chino | 1 | enclave comunitario con límites documentados (vía D) | documental |
| resto con envolvente publicada | 20 | envolvente editorial del Atlas (R02…R22) | editorial |
| `PGF2_*` | 6 | polígono del barrio (GCBA) | administrativa |
| Bajo Belgrano / Belgrano R | 2 | **sin soporte** | el control de ayer las declaró `sin_resolucion` y sigue valiendo |

**Consecuencia que se declara antes:** `locales_x_ha` es comparable **dentro** de una familia de
soporte, no entre familias. Un barrio entero y un polo de HDBSCAN no se miden con la misma vara.
La elongación, en cambio, es adimensional y aguanta mejor el cruce — pero también depende de qué
recorta el soporte, y eso se dice al lado del número.

---

## 3 · TAREA 2 · El índice de corredor

### 3.1 · La definición, fijada antes de mirar ningún resultado

Sobre la nube de puntos del soporte, en EPSG:5347:

```
PCA de las coordenadas → autovalores λ1 ≥ λ2 ;  σ1 = √λ1 , σ2 = √λ2

ÍNDICE      elongacion = σ1 / σ2          ← el índice. Es «largo sobre ancho».
```

Acompañan, **declaradas acá y no elegidas después**, como diagnóstico y no como sustitutos:

| columna | qué mide |
|---|---|
| `frac_banda_100m` | fracción de puntos a ≤100 m del eje principal (una cuadra de ancho) |
| `ancho_p80_m` | percentil 80 de la distancia al eje: el ancho absoluto, en metros |
| `largo_p5_p95_m` | recorrido sobre el eje entre los percentiles 5 y 95 |
| `elongacion_rect` | largo/ancho del rectángulo rotado mínimo **del polígono**, no de los puntos |

**Muestra mínima: 20 puntos.** Con menos, un eje principal es ruido y el índice sale `NA` con el
motivo escrito. Fijado antes, no se relaja para rescatar ninguna zona.

### 3.2 · El corte, y de dónde sale

```
corte declarado:   elongacion >= 2,0
```

Es una **convención geométrica** —dos veces más largo que ancho—, anclada afuera de los datos que
va a juzgar, como pide R3. **No sale de mirar el histograma de las 22.** Si al aplicarlo un caso
conocido cae del lado equivocado, se anota como divergencia y se explica; no se mueve el corte.

### 3.3 · Las familias que se comparan · **y una corrección al enunciado**

`cotejo_22_zonas_final.csv`, columna `familia`, tiene **seis** zonas declaradas «Eje o corredor»,
no cinco. La sexta es **R20 García del Río**, que además `QUE_ES_UN_POLO.md` §5 nombra como
corredor emergente. Se calibra contra las **seis**, y se reporta también el resultado contra las
cinco del enunciado para que la diferencia se vea.

```
Eje o corredor (6)   R02 Corrientes · R11 Bulevar Caseros · R14 Av. Boedo ·
                     R16 Donado-Holmberg · R19 Federico Lacroze · R20 García del Río
Polo (6)             R03 San Telmo · R05 Belgrano · R06 Recoleta · R08 Villa Crespo ·
                     R13 Abasto · R15 Devoto
contexto (10)        multiparte (5) · referencia dispersa (4) · área segmentada (1)
```

> **Corrección de esta enumeración, hecha después de correr y anotada como corrección.** La
> primera versión de este archivo listaba 5 «Polo» y se olvidaba **R13 Abasto**, que en el cotejo
> es familia «Polo». Son 6 y 6. La corrección no toca el corte, ni la regla, ni las tres ramas:
> sólo arregla la lista. Se deja escrita porque borrarla sería fingir que estaba bien.

### 3.4 · La lectura, con sus tres ramas

```
A · las 6 «Eje o corredor» >= 2,0  Y  las 5 «Polo» < 2,0
       -> el índice sirve, se adopta y se aplica a las 94

B · se mezclan, pero hay separación parcial: AUC(corredor vs Polo) >= 0,80
       -> se publica el índice con su curva y NO decide solo; acompaña al criterio

C · AUC < 0,80
       -> el índice no sirve. Se dice, se aplica igual a las 94 como descriptivo declarado
          inservible para decidir, y se busca otro. NO se mueve el corte: eso es lo que R3 prohíbe.
```

AUC es la probabilidad de que un corredor tomado al azar tenga índice mayor que un «Polo» tomado
al azar. 0,80 también es convención declarada, no descubierta.

### 3.5 · La circularidad, declarada antes de que aparezca

**Las 22 envolventes son dibujos editoriales.** A una zona que alguien decidió llamar corredor se
le dibujó una franja, y los puntos adentro de una franja salen elongados por construcción. Si el
índice «funciona» sólo por eso, está leyendo la mano del cartógrafo y no el territorio — y sobre
las 94, cuyos polígonos salen de un procedimiento uniforme, no transfiere.

Se mide y se declara ahora:

```
rho de Spearman entre `elongacion` (puntos) y `elongacion_rect` (polígono)

  rho >= 0,80   -> calibración CONTAMINADA. El veredicto se reporta igual, con esta salvedad
                   pegada al lado, y la adopción sobre las 94 queda condicionada.
  rho <  0,80   -> los puntos dicen algo que el dibujo no fuerza. Calibración limpia.
```

### 3.6 · La curva (R4)

El resultado depende de un parámetro elegido a mano —los 100 m de la banda—, así que la corrida no
está completa sin el barrido: `frac_banda` a 50, 75, 100, 150 y 200 m, y el ranking completo de las
22 con la familia al lado.

---

## 4 · TAREA 1 · Las columnas medibles de las seis vías

### vía A · densidad y continuidad

`n_locales`, `ha`, `locales_x_ha`, y **tres** medidas de continuidad, porque una sola no alcanza:

| columna | parámetro | por qué |
|---|---|---|
| `cont_pct_comp_mayor_60m` | 60 m, convención | % de locales en la componente conexa mayor. 60 m ≈ media cuadra: la distancia a la que dos locales están «en el mismo tramo» |
| `vecino_medio_m` | ninguno | distancia media al vecino más cercano |
| `vecino_obs_sobre_poisson` | ninguno | el observado sobre el 1/(2√λ) de Poisson. <1 = más agrupado que el azar |

La curva del primero se publica a 20, 40, 60, 80 y 120 m (R4). Los otros dos no tienen parámetro y
por eso están: si el de 60 m y los sin parámetro se contradicen, el parámetro es la mitad del
resultado y hay que decirlo.

**Regla de vía A abierta:** hay al menos un polo del borrador con **≥50 % de sus locales dentro del
soporte**. No es un umbral nuevo de cantidad: el piso de 40 locales ya está anclado en la zona
publicada más chica del Atlas, y el 50 % es la convención «más de la mitad, pertenece». Curva a
25 %, 50 %, 75 % y 100 %.

### vía B · trayectoria e instituciones

Hitos dentro del soporte, **desagregados por tipo**, desde `hitos_capa_unificada` con la lista de
Bares Notables ya corregida por la Tarea 3:

```
hitos_bar_notable · hitos_restaurante_iconico · hitos_pizzeria_emblematica ·
hitos_heladeria_historica · hitos_michelin · hitos_50best · hitos_patrimonio_normativo
```

**Límite declarado antes de contar:** sólo se pueden ubicar los hitos **con coordenadas**. La capa
tiene 211 y 181 con punto; los 30 sin punto —20 pizzerías, 5 heladerías, 4 mercados, 1 MICHELIN—
**no se ubican en el centroide del barrio**. La cobertura por tipo viaja al lado del conteo, no al
pie (corolario de R7). Un `0` en `hitos_pizzeria_emblematica` puede ser «no hay» o «no sabemos
dónde», y la tabla tiene que dejar ver cuál.

**Aviso R8 sobre `hitos_patrimonio_normativo`:** en la capa actual sólo dos registros llevan una
distinción patrimonial normativa —Mercado de San Telmo (Monumento Histórico Nacional, Decreto
12/2001) y Yiyo el Zeneize (Ley CABA 6.533)—. La Esquina Homero Manzi, que Diego cita como Sitio
Histórico Nacional, **está en la capa sólo como Bar Notable**. La columna va a salir casi entera en
cero y eso es un hueco de la fuente, no un resultado sobre el territorio. Se dice fuerte.

**Regla de vía B abierta:** ≥1 hito de cualquier tipo dentro del soporte.

### vía C · mercados y centralidades

`mercado_patio_dentro` (si/no) y `mercado_patio_cual`. Fuente: los 12 `Mercado/patio` de la capa,
de los cuales **8 tienen coordenadas**. Gourmand Food Hall, Mercado San Nicolás, Mercat Villa
Crespo y Smart Plaza Parque Patricios no tienen dirección en ninguna de las dos fuentes: entran
declarados como no ubicables. **Regla:** ≥1 mercado o patio dentro.

### vía D · comunidades y especialización

Los cuatro enclaves con límites documentados que dio Diego, construidos desde el callejero oficial
del GCBA (`callejero_gcba_2026_06_02.geojson`):

| enclave | tramos |
|---|---|
| Barrio Chino | Arribeños entre Juramento y Olazábal; Mendoza entre Montañeses y las vías |
| Barrio Coreano Baek-ku | Av. Carabobo entre Castañares y Eva Perón |
| Pasaje Ruperto Godoy | entre Helguera y Cuenca |
| Microcentro boliviano de Liniers | José León Suárez desde Rivadavia; Falcón, Ibarrola, Gral. Paz |

Cada enclave es la unión de esos tramos **con un buffer de 150 m** —una cuadra a cada lado del
eje—, declarado como convención y publicado con su curva a 50, 100, 150, 200 y 300 m (R4).
«Las vías» del tramo de Mendoza se resuelve con el cruce a nivel que el propio callejero marca en
`tipo_ffcc`; si no aparece, se declara y se corta por el extremo del tramo, sin inventar.

**Regla de vía D abierta:** el soporte intersecta ≥1 enclave.

### vía E · reconocimiento externo

**La columna queda vacía.** La llena Diego desde afuera. No se estima, no se infiere, no se rellena
con proxies.

### vía F · corredor

El índice de la Tarea 2, más `forma_declarada` derivada del corte **sólo si la Tarea 2 lo adopta**.
Si el veredicto es B, la columna se publica y no decide. Si es C, la columna se publica marcada
como no apta para decidir.

---

## 5 · TAREA 4 · El control nuevo sobre las 22

Cuántas vías **medibles** (A, B, C, D, F — la E no, que la llena Diego) abre cada una de las 22
zonas publicadas, sobre su envolvente editorial.

Lectura, la de Diego, tal cual:

```
todas las 22 abren al menos una vía medible  -> la grilla se sostiene sola
algunas sólo abren la vía E                   -> la grilla depende del trabajo documental,
                                                 y hay que decirlo
alguna no abre ninguna                        -> hay un error de cálculo. Se busca antes de seguir
```

Y una nota que se escribe antes por si aparece: si una zona abre **cero** vías, el primer sospechoso
no es el territorio sino el soporte —una envolvente de 1 % de cobertura como la de R20 puede no
contener ni sus propios locales—. Ese diagnóstico se mide, no se supone.

---

## 6 · TAREA 3 · Los tres cierres

**a)** Se fusionan los pares de homónimos con la misma altura. **Aviso antes de correr:** los «4
pares» impresos son **3 bares** —Café Palacio aparece en dos líneas porque la entidad ya fusionada
tiene dos nombres—, y de los tres, sólo Café Palacio queda en las tres listas. Bar Bidou junta
Wikidata + Boletín y El Preferido de Palermo junta GCBA + Wikidata: los dos quedan en **dos**
listas. La predicción del enunciado es 70 → 74; **lo que la fusión puede dar es 70 → 71**, y se
reporta lo que salga, con el desglose bar por bar.

**b)** El **Boletín Oficial** pasa a ser la lista canónica de Bares Notables, por ser la
declaratoria. Los que sólo tiene Wikidata quedan en un archivo aparte con su origen, **no se
descartan**. Después de las fusiones dejan de ser 11.

**c)** La matriz ya está bajo control de versiones desde el commit `aea2cdc`. Se confirma y las
columnas nuevas entran versionadas.

---

## 7 · Las siete preguntas, contestadas de antemano

1. **¿Estaba escrita la lectura antes de correr?** Sí: este archivo, con fecha anterior a la corrida.
2. **¿Ablación con control aleatorio?** No hay ablación en esta tanda.
3. **¿Algún umbral se movió?** Los cortes —2,0 de elongación, 0,80 de AUC y de rho, 60 m de
   continuidad, 150 m de buffer, 50 % de pertenencia, 20 puntos de muestra mínima— están fijados
   acá y no se tocan después.
4. **¿Curva donde hay parámetro?** Sí: banda del eje, umbral de continuidad, buffer de enclave y
   pertenencia al soporte, las cuatro con barrido.
5. **¿Presupuesto?** Cero requests pagos. Nada que reportar contra estimado.
6. **¿«No existe» donde va «no encontramos»?** La cobertura por tipo de hito y la lista de
   mercados sin dirección van al lado de cada conteo, por eso.
7. **¿Algún campo pedido llegó vacío entero?** `hitos_patrimonio_normativo` está avisado como
   casi vacío por hueco de fuente. Si llega vacío **entero**, la corrida lo dice y no se reporta
   ninguna conclusión sobre esa columna.
