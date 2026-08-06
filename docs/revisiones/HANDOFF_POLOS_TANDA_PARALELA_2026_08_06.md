# HANDOFF · Tanda paralela: nombrar, poligonizar, Soho y el corte de la serie R8 · 2026-08-06

Continúa `HANDOFF_POLOS_P078_CERRADO_2026_08_06.md`. Rama `mercados-gastronomicos-v2`.
**Commiteado en 8 etapas** (antes estaba todo suelto). **Google Places: 0 requests.** Ninguna
cifra publicada tocada.

Scripts nuevos: `polos_para_nombrar.py`, `inventario_nombres_de_calle.py`,
`auditar_uniones_por_envolvente.py`, `polos_donde_esta_soho.py`, `polos_poligonizar.py`.

---

## 1 · TAREA 0 · `POLOS_PARA_NOMBRAR.csv` — entregada

124 filas con las 13 columnas pedidas. Tres van con advertencia al lado y no al pie:

- `calles_dominantes` no es censo por calle. **54 de 124 polos tienen menos de la mitad de sus
  locales con dirección**; ahí las calles no alcanzan solas.
- `distancia_al_corte` mide distancia a una **convención**, no a una frontera. 15 polos están a
  menos de 0,5 loc/ha del corte: en ésos la clase no debería entrar en el nombre.
- `d_al_vecino_entre_puntos_m` es **entre puntos**. 6 polos están a menos de 50 m de otro.

**62 de 124 polos no tienen ninguna zona publicada encima** (4.678 locales): se nombran desde cero.

## 2 · La regla 4 del hull, y las dos uniones firmadas NO se recorren

`CUANDO_DOS_POLOS_SON_UNO.md` §4: *toda decisión de unir se toma entre puntos; la distancia entre
envolventes se reporta al lado y no decide.*

Reauditados los 35 pares candidatos. **7 de 35 cambian de lado del corte de 50 m** según la
columna; el factor máximo es **7,4×** (P091+P088: 16,2 m de envolvente, 119,4 entre puntos).

Las dos uniones firmadas se sostienen, y el motivo importa más que la conclusión: la distancia
entre envolventes **nunca decidió** una unión —sólo elegía qué pares se evaluaban—, y las decidieron
continuidad y estabilidad, que corren sobre puntos. Además el filtro por envolvente peca de ancho
y nunca de angosto, así que no se perdió ninguna candidata. **Lo que cambia es la cita:**
P090+P089 está a **21,6 m** (no 15,1) y P101+P099 a **85,2 m** (no 85,1).

## 3 · TAREA 2 · Soho es P091 — y las tres subzonas estaban

Se cumplió el **primer** caso de la lectura declarada. La esquina Serrano y Honduras cae adentro
del polígono de P091; el local asignado más cercano está a 2 m y es de P091. Las cuatro calles de
Soho están entre las once primeras del polo y Armenia es la segunda.

| | |
|---|---|
| Palermo Soho | **P091** (728 locales) |
| Palermo Hollywood | **P078** (585) |
| Las Cañitas | **dentro de P065** (Báez 17/17, Arce 17/17) |

**La hipótesis acertaba los lugares y erraba la forma.** Palermo no es un polo que se parte en
tres: son varios polos, y tres llevan los nombres de uso corriente. Por eso ninguna curva de
estabilidad los encontraba — se los buscaba adentro de un polo en vez de entre polos.

Corregida la nota de `polos_p065_union_y_clases.py` que decía que Cañitas no estaba en P065.

## 4 · La serie R8, cortada con inventario

El bicho dominante es **la continuación directa de Niceto Vega**: al desinvertir la coma, el
marcador que estaba al final del último segmento queda **en el medio**. `CALVO, CARLOS AV.` →
`CARLOS AV. CALVO`, donde ninguna regla de extremos lo alcanza. Aparecía en **23 avenidas**.

Y dos que nadie había visto: **mojibake de dos vueltas** (Arribeños en seis grafías) y **códigos
postales** pegados al nombre.

| | antes | después |
|---|---:|---:|
| grupos de claves que son la misma calle | 101 | **46** |
| direcciones afectadas | 2.815 | **1.025** |

**Residuo declarado, no olvidado:** las iniciales no se tocan. `RAMON L. FALCON` y `RAMON FALCON`
siguen separadas, porque tirar las letras sueltas rompería `S. MARTIN`, que es *San* Martín y no
una inicial. Sin callejero canónico no se distinguen. 23/23 tests pasan.

*Efecto visible en Tarea 0:* Scalabrini Ortiz pasó a ser la calle N.º 1 de P091 — antes estaba
partida en dos y no entraba al top 6.

## 5 · TAREA 3 · Poligonización

Cuatro criterios declarados antes de correr. **Cóncavo** (el convexo reclama parques y vías, y las
22 envolventes publicadas no son convexas). **El ratio no cambia**: 0,55 ya produjo todas las
superficies y clases que existen.

La curva: de **1.016 ha** en el extremo cóncavo a **3.958** en el convexo (**3,9×**). Pero en
±0,15 alrededor de 0,55 el área se mueve **22,4 %** y sólo **10 de 124** polos cambian de clase.
No está parado en un borde. Aun así **la superficie de un polo es una medida a este ratio** y se
cita así.

**Sin simplificar**, y con la parte incómoda dicha: la regla declarada iba a elegir 0 sí o sí,
porque los vértices de una envolvente de puntos *son* los locales. **No discriminó nada.** Lo que
sostiene el 0 es independiente: 15,9 vértices por polo, más simple que el extremo simple de lo
publicado.

**Sin recorte a manzana**, y es carencia y no preferencia: no hay capa de manzanas ni parcelas en
el repositorio.

Capa nueva: `polos_publicables.geojson`. `borrador_polos_v3.geojson` no se tocó.

---

## Trampas encontradas hoy

- **`within` excluye el borde.** Los vértices del hull son los locales, así que medido con `within`
  el polígono sin simplificar «expulsaba» 1.853 de sus propios locales — imposible por
  construcción. El número era plausible y la conclusión también («no se puede simplificar»): **la
  respuesta equivocada llegaba disfrazada de respuesta conservadora.** Va `covered_by`.
- **Una condición dura puede cumplir la forma de un criterio sin hacer su trabajo.** La regla de
  simplificación era insatisfacible por construcción para esta familia de geometrías. Conviene
  preguntarse, al escribir una condición declarada, si puede dar algo distinto de la respuesta
  trivial.
- **Un grep que devuelve vacío no es una verificación.** Reporté «cero place_id» y estaba mal: el
  comando había fallado en silencio. Rehecho por lotes, aparecieron 6 archivos.
- **`git add -A` barrió 7.160 archivos**, incluidas las tablas internas de Places de fase11 con
  `place_id` real. Revertido antes de pushear (nada se pusheó: `origin` seguía en `e6d79a9`). Ya
  tienen regla en `.gitignore`: **lo que protege un archivo es el .gitignore, no la prolijidad.**

## Lo que espera decisión

1. **TAREA 1 está bloqueada: falta `hitos_documentales_caba.csv`.** No está en el repositorio. No
   se inventa. Lo que sí existe y ya está geocodificado por USIG es **Bares Notables** (Wikidata,
   CC0), que cubre una de las seis capas.
2. **Los ~7.000 archivos sin rastrear** del repositorio: qué se versiona y qué no. Los de Places
   ya quedaron excluidos por regla.
3. Sigue de antes: el saliente N–NE como hallazgo, R01 en la V3 con el 47,7 %, el borrado de
   `places_resumen_por_barrio.csv`, R15 Devoto, R04 Puerto Madero, la cláusula ODbL, el visto de
   Patricia, Bares Notables contra la normativa, Foursquare, y el documento extenso del método.
