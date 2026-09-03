# HANDOFF · P078 cerrado, el saliente medido y el registro bajo el mínimo · 2026-08-06

Continúa `HANDOFF_POLOS_DECISIONES_Y_METODO_2026_08_06.md`. Rama `mercados-gastronomicos-v2`.
**Sin commit.** Ninguna cifra publicada tocada; el Atlas no se tocó. **Google Places: 0 requests.**

Scripts nuevos: `polos_saliente_p078_de_quien_es.py`, `polos_p078_prueba_estabilidad.py`,
`polos_candidatos_bajo_minimo.py`.

**P078 queda cerrado, y va entero.** No por la excepción refutada sino por la prueba de
estabilidad, que es la que correspondía y nunca se le había corrido.

---

## 1 · La excepción, registrada como refutada

En `DECISIONES_P078_P103_2026-08.md` y en `borrador_polos/MATRIZ_DECISION_BORRADOR.csv`, con los
números al lado y sin borrar: `P078-EXC · REFUTADO`. Y **el motivo no se reemplazó por otro.**

## 2 · Prueba de estabilidad · ARBITRARIA · P078 entero

Lectura declarada antes de correr. Grilla de 5 m, porque la lectura está escrita en metros de
rango y la grilla vieja tenía un salto de 40 m justo del ancho de la ventana a evaluar. **Ninguna
vara cambió: cambió el instrumento.**

| condición | exige | resultado | |
|---|---|---|---|
| n.º de partes = 3 en un rango | ≥ 60 m | tramo 40–60 m = **20 m** | **NO CUMPLE** |
| el n.º no cambia en ±40 m de 55 m | 15–95 m | toma **0, 1, 2 y 3** | **NO CUMPLE** |
| 4+ piezas comparables | — | no aparecen | no se reabre |

La curva, formato Belgrano:

| umbral | 35 | **40** | 45 | 50 | **55** | 60 | 65 | 75 | 90 |
|---|---|---|---|---|---|---|---|---|---|
| partes | 107 | 183;46;41 | 291;41;40 | 325;46;40 | **333;88;41** | 379;92;43 | 491;47 | 555 | 585 |
| pct | 18,3 | 46,2 | 63,6 | 70,3 | **79,0** | 87,9 | 92,0 | 94,9 | 100 |

Es literalmente el motivo por el que se rechazó BEL-B —«elegir cuatro sería arbitrario»— con la
curva al lado.

### Prueba 3 · y acá aparece lo que no esperaba nadie

| parte | calles dominantes |
|---|---|
| S1 (333) | Bonpland · Fitz Roy · Costa Rica · Honduras · Humboldt · Gorriti |
| S2 (88) | Dorrego · Arévalo · Gorriti · Niceto Vega · J. A. Cabrera · Álvarez Thomas |
| S3 (41) | Niceto Vega · Humboldt · Fitz Roy · Bonpland · Córdoba |

**S1 y S3 comparten Humboldt, Fitz Roy y Bonpland: son el mismo lugar partido por Av. Niceto
Vega.** No son dos centralidades distintas.

Y el dato que cierra la hipótesis de origen: **no aparece ninguna calle de Palermo Soho** —ni
Serrano, ni Thames, ni Armenia, ni Borges—. **P078 no es Soho + Hollywood + Cañitas: es Palermo
Hollywood y su borde norte.** Sumado a que P091 tampoco se descompone, la hipótesis de las tres
subzonas de Palermo no está en el borrador por ningún lado.

*La evidencia de calles sale de 161/333, 51/88 y 18/41 locales con dirección, y no hay callejero
canónico detrás.*

## 3 · El saliente no es de nadie · hallazgo acotado

Los tres bloques contra **todos** los polos del borrador:

| bloque | más cercano | envolventes | **entre puntos** | polo externo más cercano |
|---|---|---:|---:|---:|
| bloque_35 | P078·S1 | 11,3 m | **55,8 m** | 315,7 m |
| bloque_23 | P078·S1 | 75,0 m | 102,2 m | 175,1 m |
| bloque_12 | P078·S1 | 25,8 m | 80,2 m | 287,8 m |

**Ningún bloque bajo 50 m: el precedente Recoleta no aplica.** El mínimo no se movió. Va como (c),
con redacción R7:

> Concentración lineal de 108 locales al norte-noreste de Palermo Hollywood, orientada (R = 0,70,
> rumbo 36°), **el 88 % fuera de toda zona publicada**. Su bloque mayor —35 locales— no alcanza el
> mínimo declarado de 40 por 5 locales. Con la cobertura y el umbral declarados no califica; **eso
> no es una afirmación sobre la actividad del área.**

## 4 · `CANDIDATOS_BAJO_MINIMO.csv` · 17 conglomerados, 496 locales

14 fuera de todo polo (405 locales) + 3 bloques internos (91). Con id, locales, barrios, comuna,
polo más cercano y sus dos distancias, y zona publicada.

**Léase la sensibilidad ANTES que la tabla:** el conteo pasa de **1 a 40 m, a 14 a 55 m, a 18 a
70 m**. El registro es lo que se ve con un umbral de contigüidad de 55 m, **no una propiedad del
territorio**, y quien lo cite tiene que citar el umbral en la misma frase.

Y sobre el sur, escrito con cuidado porque es donde el Atlas se equivocó: con este umbral **no
aparecen** conglomerados de 25–39 locales en las comunas 4, 8 ni 9 — la oferta que la base
registra ahí ya quedó adentro de polos que sí califican. **No es una afirmación sobre la actividad
del sur.**

## 5 · R01 · el hallazgo colateral, con el número corregido

**El 21 % no era el número de esto.** Ése es la fracción de P078 que queda fuera de sus tres
partes, que es otra pregunta. Contra el polígono publicado:

- **279 de los 585 locales de P078 caen fuera de R01: el 47,7 %.**
- Y R01 no es «el polígono de P078»: es una zona multiparte de 2,71 km² con **1.358** locales de
  la base adentro, de los cuales sólo **306** son de P078.

La relación no es uno a uno **en ninguna de las dos direcciones**. Va a la conversación de la V3
con ese número, no con el 21 %.

## 6 · Material · 40 → **47 archivos**

Las tres pruebas, el saliente, el registro bajo el mínimo con su sensibilidad, y la matriz de
decisión con la excepción refutada adentro.

---

## Trampas encontradas hoy

- **La distancia entre envolventes puede ser mucho menor que la distancia entre puntos, y unir por
  la primera es un error.** bloque_35 daba 11,3 m entre envolventes —debajo del corte de 50 m de
  Recoleta— y 55,8 m entre puntos. El borde de un hull es un segmento tendido entre dos puntos
  lejanos, y un tercero puede pasar cerca de ese segmento sin estar cerca de ningún punto. **Con
  la columna equivocada, el saliente se unía y P078 pasaba.** Toda decisión de unir se toma con la
  distancia entre puntos.
- **Medir un bloque contra el polo que lo produjo es un sesgo de procedencia**, y además la
  envolvente del polo lo contiene, así que da 0 por construcción. Había que medirlo contra los 124.
- **La inversión de nombres de calle puede tener más de una coma.** `VEGA, NICETO, Cnel. AV.` es
  Avenida Coronel Niceto Vega; con un solo `split(",", 1)` quedaba como «NICETO, CNEL. VEGA» y se
  contaba aparte de «Niceto Vega» — la misma calle en dos filas con la mitad de los locales cada
  una. **Tercer bicho de la familia de R8 en dos días.** Arreglado, con el caso en el test (14
  casos, todos pasan).
- **Un separador que también aparece adentro de los datos no es un separador.** La lista de calles
  se unía con `", "` y hay nombres con coma: no se podía saber dónde terminaba una entrada. Ahora
  va con ` · `.
- **Una tabla cuya sensibilidad al parámetro es 1 → 14 → 18 no se publica sin la sensibilidad
  arriba**, no al pie.

## Lo que espera decisión

1. **Qué se hace con el saliente N–NE** como hallazgo: si entra al informe con la redacción R7 de
   §3 o queda sólo en el registro.
2. **R01 en la V3**, con el 47,7 % y la no-correspondencia en las dos direcciones.
3. **Dónde está Soho**, si es que está: no aparece ni en P078 ni en P091. Es una pregunta nueva
   que abrió la prueba 3.
4. El borrado chico de `places_resumen_por_barrio.csv`, que sigue pendiente de confirmación.
5. Siguen de antes: R15 Devoto, R04 Puerto Madero, las tres zonas en E3, la cláusula ODbL, el visto
   de Patricia, Bares Notables contra la normativa, Foursquare.
6. **El documento extenso del método**, con el material de §6.
