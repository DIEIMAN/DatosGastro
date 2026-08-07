# HANDOFF · Las seis vías, el índice de corredor y el control de las 22 · 2026-08-07

Continúa `HANDOFF_POLOS_DOSSIER_Y_MATRIZ_2026_08_06.md`. Rama `mercados-gastronomicos-v2`.
**Google Places: 0 requests.** Ninguna geometría publicada tocada. Ninguna cifra del Atlas tocada.

Base de todo: `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/QUE_ES_UN_POLO.md` (definición de
Diego, 2026-08-07). La lectura de las tres corridas se escribió **antes** de correr, en
`outputs/BARRIDO_CIUDAD_2026-08/seis_vias/LECTURA_PREVIA.md`.

**El informe completo está en `outputs/BARRIDO_CIUDAD_2026-08/seis_vias/INFORME_SEIS_VIAS.md`.**
Esto es el resumen para retomar.

---

## Qué se produjo

Scripts nuevos, todos en `scripts/barrido_ciudad/`:

| script | qué hace |
|---|---|
| `polos_soporte.py` | el soporte geométrico de cada fila + los cuatro enclaves desde el callejero |
| `polos_indice_corredor.py` | Tarea 2: el índice, la calibración contra las 22, el veredicto |
| `polos_seis_vias.py` | Tarea 1 y Tarea 4: las columnas medibles y el control de las 22 |
| `polos_matriz_seis_vias.py` | incorpora las columnas a la matriz verificando las viejas |
| `hitos_cerrar_bares_notables.py` | Tarea 3a y 3b: fusiones y canon del Boletín |

Salidas en `outputs/BARRIDO_CIUDAD_2026-08/seis_vias/` y `.../hitos/`.
**La matriz pasó de 23 a 51 columnas**, con las 23 viejas verificadas contra `git HEAD`:
**0 celdas distintas**.

---

## Los cuatro resultados, en una línea cada uno

1. **Índice de corredor · RAMA B.** Las 6 declaradas corredor quedan arriba del corte de 2,0; de
   las 6 «Polo», Abasto (2,61) y Devoto (2,42) lo cruzan. AUC 0,972. **Se publica con su curva y
   no decide solo.** El corte no se movió.
2. **Las seis vías, medidas sobre las 94.** A abre 89, B 40, C 4, D 7, F 53. **E queda vacía: la
   llena Diego.**
3. **El control de las 22: las 22 abren al menos una vía medible. Ninguna en cero.** Por la
   lectura declarada, **la grilla se sostiene sola**.
4. **Los homónimos: «en las tres listas» da 71, no 74.** Estaba avisado antes de correr y el
   motivo también.

---

## Las tres cosas que hay que leer antes de usar los números

**La calibración del índice está contaminada, y se midió.** rho de Spearman entre la elongación de
los puntos y la del polígono: **0,949**. Las envolventes son dibujos editoriales; a lo que se
decidió llamar corredor se le dibujó una franja. El índice lee bien la forma que hay, y eso no es
lo mismo que descubrirla.

**A la escala del polo del borrador, «corredor» es la regla.** Mediana de elongación 2,23 sobre un
corte de 2,0: **63 % de los polos dan corredor**. `via_F_forma` sirve sobre las envolventes y **no
discrimina sobre los polos**. No usarla ahí para decidir.

**Las dos medidas de continuidad no se ponen de acuerdo** (Spearman 0,634). La de 60 m depende del
tamaño del soporte —Barrio Chino 97,3 %, Flores 6,1 %—; la razón observado/Poisson no. Entre
soportes distintos, usar la de Poisson.

---

## Los huecos de fuente que la corrida dejó a la vista

- **20 pizzerías emblemáticas y 5 heladerías históricas: cero coordenadas.** Vienen con nombre y
  barrio, sin altura. Un `0` en esas columnas significa «no sabemos dónde», no «no hay». Es el
  caso de la pizzería San Antonio que la definición cita para Boedo.
- **`via_B_patrimonio_normativo` tiene 2 hitos en toda la Ciudad**: Mercado de San Telmo (Decreto
  12/2001) y Yiyo el Zeneize (Ley 6.533). **La Esquina Homero Manzi figura sólo como Bar Notable**:
  su condición de Sitio Histórico Nacional no está cargada en ningún archivo del repositorio.
- **El ex-Mercado de Abasto no está en el listado oficial de mercados y patios**, así que R13 no
  abre vía C aunque la definición lo use como su ejemplo de vía C.
- **El Mercado de San Telmo queda 64 m afuera de la envolvente R03.**
- **El enclave de Liniers es el único que la delimitación no cierra** («José León Suárez desde
  Rivadavia; Falcón, Ibarrola, Gral. Paz»). Salió de 104 ha leyéndola literal.

---

## La corrección al enunciado que hay que registrar

**Av. Boedo no tenía «cero señal de concentración».** La sonda de calle de ayer veía 17 locales
sobre la calle Boedo; la envolvente publicada R14 tiene **245 locales y 2 polos** (P029, P062).
Boedo abre **A, B y F**. El caso sigue probando que el descarte estaba mal —y por eso la
definición nueva es correcta— pero no por falta de densidad: **por una sonda que medía el frente
de la avenida y no la zona.**

Y dos de enumeración: las declaradas «Eje o corredor» son **6** (entra R20 García del Río) y las
«Polo» también **6** (entra R13 Abasto).

---

## Trampas encontradas hoy

- **Un filtro que no matchea nada devuelve un veredicto perfecto.** La primera pasada del índice
  comparó la etiqueta corta del geojson (`eje`, `polo`) contra la larga del cotejo. Las dos
  familias quedaron vacías y **la condición de la rama A se cumple trivialmente sobre conjuntos
  vacíos**: la corrida terminó sin error y declaró que el índice servía. Ahora corta.
- **Un merge que colisiona se queda con la columna vieja.** Al reincorporar a la matriz,
  `n_vias_medibles` existía en los dos lados; pandas dejó la vieja con su nombre y la nueva con
  sufijo, y el reporte anunció haber escrito la nueva. Se borran las columnas de destino antes de
  unir.
- **El centroide de una calle no es dónde cruza.** Gral. Paz rodea la Ciudad; proyectar su
  centroide sobre José León Suárez devolvió un tramo de 10 m sin fallar.
- **Un patrón demasiado ancho vacía de sentido una columna.** Buscar «Ley» para patrimonio
  normativo trajo los 90 bares notables: su distinción es la Ley 35.
- **Un `0` en una columna derivada se lee como hallazgo.** `n_vias_medibles` en las dos filas sin
  soporte queda **vacío**, no cero.

---

## Lo que espera decisión

1. **La vía E**, la única columna que falta para que la grilla esté completa.
2. **`via_F_forma` sobre los polos del borrador**: aceptar que no discrimina a esa escala, o
   calibrar un corte propio anclado afuera de la distribución de los polos.
3. **Cargar el patrimonio normativo declarado**, empezando por Homero Manzi.
4. **Geocodificar las 20 pizzerías y las 5 heladerías**, o declararlas no ubicables en la tabla.
5. **Apretar el recorte del enclave de Liniers**, si 104 ha es demasiado.
6. **Ampliar la fuente de la vía C** si el criterio incluye centralidades fuera del listado oficial.
7. **La envolvente R03 de San Telmo**, que deja su mercado 64 m afuera.
8. **Los 8 bares que tienen GCBA y Wikidata y el Boletín no**: son los que más merecen que alguien
   mire el acto administrativo.
9. Sigue de antes: las 39 filas nuevas que superponen territorio de una vieja, `Ultramarinos` sin
   geocodificar, `Mercado San Nicolás` y `Smart Plaza Parque Patricios` sin dirección, los ~7.000
   archivos sin rastrear, el saliente N–NE, R01 en la V3 con el 47,7 %, R15 Devoto, R04 Puerto
   Madero, la cláusula ODbL, el visto de Patricia, Foursquare y el documento extenso del método.
