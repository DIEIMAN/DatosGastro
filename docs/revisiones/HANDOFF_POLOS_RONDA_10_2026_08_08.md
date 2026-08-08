# HANDOFF · Ronda 10 · La compuerta, el callejero canónico y la fuente que no se cayó · 2026-08-08

Continúa `HANDOFF_POLOS_RONDA_9_2026_08_08.md`. Rama `mercados-gastronomicos-v2`.
**Google Places: 0 requests.** Llegaron los diecinueve archivos de cowork.

---

## 1 · Places: la compuerta está construida, y no se gastó nada

`scripts/barrido_ciudad/places_compuerta_identidad.py` + 14 tests. Las cuatro condiciones:

- **(a)** `CAMPOS_MINIMOS` incluye `displayName` y `formattedAddress`, y `validar_mascara()`
  **levanta `ValueError` antes del primer request** si faltan. La máscara de la ronda 8 ahora corta
  sola: hay un test que lo comprueba.
- **(b)** `compuerta()` **rechaza**, no marca. Un rechazado devuelve `business_status = ""` — no es
  un `OPERATIONAL` débil, es la ausencia de dato. Se reusa el control de dirección de la ronda 8,
  que de 71 dejó una sola falla real, y se le suma la regla de esquina.
- **(c)** `CANDIDATOS = 5`. Se desambigua entre candidatos; y si dos son igual de buenos con
  estados distintos, se rechaza por no reproducible.
- **(d)** `contradiccion()` anula la respuesta entera cuando dos campos se contradicen.

**Validada contra los cuatro casos ya pagados**, que es la única prueba honesta que había:

| caso | esperado | la compuerta |
|---|---|---|
| Papa Frita — devolvió el preguntado | aceptar | **acepta** |
| Mercado de los Carruajes — su propio nombre, cerrado | aceptar | **acepta** |
| Castelar — «EX Hotel Castelar.» + `OPERATIONAL` | rechazar | **rechaza** (contradicción) |
| **La Perla del Once — devolvió «La Americana»** | **rechazar** | **rechaza** |

Y no rompe lo que funcionaba: El Tokio (misma cuadra) pasa, «Los Galgos (Callao 501)» pasa, Crizia
—la única alarma verdadera de las 71— sigue siendo rechazo.

**R15 cargada** en el método: *una predicción que se cumple se audita igual que una que falla*. El
caso es exactamente el de la ronda 9 — la predicción se cumplió y era otro establecimiento.

**La ronda 8 queda dada por perdida.** Repreguntar sigue esperando decisión; ahora hay con qué.

---

## 2 · Palermo: la opción A se sostiene, y el residuo tiene forma

**(a)** El padre `R01 ∪ Soho ∪ Hollywood ∪ Cañitas` contiene a los cuatro con **0,000000 m²
perdidos** cada uno. Medido por superficie, no por predicado — y bien que sí: `covers()` devuelve
`False` sobre esa misma geometría, que es la trampa de GEOS ya registrada.

El padre mide **385,51 ha · 1.916 locales**.

**La opción B perdía 108,50 ha y 188 locales publicados**, no 407. **El 407 era otra cosa**: eran
los locales de Soho ∪ Hollywood que caen *fuera* de R01, contados contra dos subzonas. Contra las
tres, y en la dirección que importa —lo de R01 que no está en las subzonas— son **188**.

**(b)** El residuo son **8 piezas**, y **no está repartido**:

| # | ha | locales | barrio dominante |
|---|---|---|---|
| **1** | **40,17** | **134** | **Palermo (100 %)** |
| 2 | 31,42 | 15 | Palermo (100 %) |
| 3 | 11,07 | 25 | Villa Crespo (88 %) |
| 4–8 | 25,84 | 14 | Palermo / Colegiales / Chacarita |

**Una sola pieza lleva el 71 % de los locales.** Es un área coherente, no un remiendo: la figura
que corresponde es un polo con subzonas y ésta es una subzona más, la que todavía no tiene nombre.

**(c)** Cuidado con dos objetos distintos: el **eje entero** de Concepción Arenal mide 3.253 m y
sólo el 8 % cae en R01; el **tramo Zapiola–Conesa** mide 143 m y es el 47 % de *su* área a 150 m lo
que cae adentro. El 47 % es del tramo. Y alcanza para decidir: **el tramo está pisado por R01 casi
a la mitad, así que no se delimita desde Colegiales sin tocar Palermo.** Sale de Z43.

---

## 3 · El callejero: no eran tres casos, son 67

`callejero_canonico.py` agrupa por raíz **y** contacto geométrico. **67 corredores están partidos
en más de un nombre oficial**, muchos muy desparejos:

    CORDOBA      286 m ( 3 %)  +  CORDOBA AV     7.877 m (97 %)
    BOEDO        539 m (17 %)  +  BOEDO AV       2.582 m (83 %)
    AVELLANEDA 2.211 m (37 %)  +  AVELLANEDA AV  3.836 m (63 %)

`test_callejero_canonico.py` — **14 pruebas con casos negativos**, que son las que importan: un
test que sólo verificara que los tres casos conocidos se unen pasaría también con una función que
une todo con todo. Los negativos: San Martín vs Av. San Martín (6,6 km), Azul vs Azul Pasaje,
Maipú vs Av. Maipú (102 m, el borde), «SOLDADO DE LA INDEPENDENCIA» vs «INDEPENDENCIA AV.», y
Esquiú —el `esq` adentro del nombre—.

**`tramo_entre()` ahora falla ruidoso.** Un corte a más de 40 m del eje levanta `AnclaFueraDelEje`
con el diagnóstico. Verificado: el caso de R20 revienta con «queda a 761 m», y **Z23 Flores, que
estaba bien, sigue dando los mismos 1.270 m**.

**Nota honesta:** de los tres casos que Diego citó, en este callejero sólo dos son splits de
nombre. `INDEPENDENCIA` existe únicamente como `INDEPENDENCIA AV.`; ese caso venía de otro lado.

---

## 4 · Parte X · los límites de la base

`outputs/BARRIDO_CIUDAD_2026-08/ronda_10/PARTE_X_LIMITES_DE_LA_BASE.md`, con las dos secciones:
el **46,6 % sin `direccion_norm`** (11.170 de 23.981) y los **67 corredores partidos**.

Lo que queda escrito como regla: cuando una pregunta necesita el nombre de la calle, el nombre se
resuelve **por geometría contra el callejero**, no por el texto; y si hay que usar el texto, el
porcentaje atribuido va en la misma tabla. Condiciona directamente el cruce con los ejes del
IDECBA, que están delimitados por calle y altura.

---

## 5 · Monserrat: el catálogo tiene razón, y la lámina 7 se libera

**Los nueve están en la capa.** Los otros siete no faltaban: **están cargados con otro
`barrio_declarado`** —casi todos `nan`—, y el conteo de 2 salía de filtrar por ese campo, que es
texto de la fuente y no geometría. **Es R13, y el que lo cometió fui yo en la ronda 9**: reporté
«Monserrat tiene 2 Notables en la capa» filtrando exactamente así.

**El límite norte es Av. Rivadavia**, medido contra la capa oficial de barrios:

- **2.045 m** del borde de Monserrat corren sobre Av. Rivadavia; **32 m** sobre Av. de Mayo.
- Monserrat contiene puntos hasta ~60–80 m al norte del eje de Av. de Mayo.
- Y los cuatro de Av. de Mayo —Iberia 1196, Tortoni 825, London City 599, Los 36 Billares 1265—
  **caen dentro de Monserrat** por posición.

**La lámina 7 se puede usar.**

---

## 6 · Las dos erratas, aplicadas

- `seis_vias_94_filas_r10.csv`: `PGR_P004` pasa a `via_C_abierta = no`. Queda con **una** vía
  geométrica abierta (la A) y las tres documentales cerradas en S_LUGANO.
- `cola_de_R20_corregida.csv`: **28,63 ha (47 %) y 31 locales (30 %)**, con las 22 calles y el
  motivo del cambio. **La frase «más de la mitad de los establecimientos están en la parte sin
  respaldo» se cae**: son el 30 %. La cola es más grande en superficie y más chica en locales.

---

## 7 · IDECBA · bajado, y trae más de lo que se pedía

`AC_EJ_2026_03.xlsx` y `AC_EJ_48_GLOS.xlsx` bajados. **Son 48 ejes vigentes, no 53** — el universo
pasó de 37 a 53 y de 53 a 48; los nombres del glosario y los del relevamiento coinciden exactamente.

**Y el archivo trae cuatro cuatrimestres**, no uno: 1.º, 2.º y 3.º de 2025 y 1.º de 2026. La
variación interanual se computa acá, sobre el mismo eje y el mismo método:

| | relevados | ocupados | ocupación |
|---|---|---|---|
| 1.er cuatr. 2025 | 12.936 | 11.843 | 91,6 % |
| 2.º cuatr. 2025 | 12.919 | 11.819 | 91,5 % |
| 3.er cuatr. 2025 | 12.898 | 11.781 | 91,3 % |
| **1.er cuatr. 2026** | **12.896** | **11.605** | **90,0 %** |

**−2,0 % de locales ocupados en un año, con la ocupación bajando los cuatro cuatrimestres
seguidos.** Los que más caen: Villa Crespo (−9,7 %), Montes de Oca (−8,4 %), Warnes (−8,4 %),
Santa Fe y Callao (−7,8 %). Los que suben: Córdoba Tribunales (+4,3 %), Av. San Martín (+4,2 %),
Defensa (+3,8 %), Flores Sur (+3,7 %).

**27 de los 48 están en el Atlas; 20 no.** El cruce es **nominal y se declara como tal**: el IDECBA
delimita por calle y altura y la base tiene el 46,6 % sin dirección. Para atribuirle a una zona la
tasa de su eje hay que construir los 80 tramos del glosario como geometría — es lo que sigue.

### Lo que faltaba del .xlsx, entregado

`idecba_densidad_48_ejes.csv` — **locales relevados, cuadras y densidad comercial** por eje, que es
lo que permite calibrar contra la vía A. Las cuadras no vienen como columna: se derivan de
`relevados ÷ densidad`, y el cociente cierra contra el total declarado (13,81 locales por cuadra).

Los más densos: Avellaneda 23,33 por cuadra (1.073 locales en 46 cuadras), Libertad 22,80, Flores
Sur 20,17. Los menos: Puerto Madero 2,23 y Recoleta 5,94.

**No se comparan de prepo con la vía A**: el IDECBA mide locales por CUADRA sobre un eje lineal y
la vía A mide locales por HECTÁREA sobre un polígono. Habilita calibración, no equivalencia.

### El PDF de 53 ejes es OTRA EDICIÓN, no otra lectura

Probado contra los cuatro cuatrimestres del `.xlsx`, el PDF **no coincide con ninguno** (el más
cercano, 2025 c3, tiene 13 de 47 dentro de 0,1 pp y mediana de 0,70 pp). Trae los **53 ejes del
universo anterior**; sus tasas son de su propio período y **no se mezclan con las de 2026**.

**Y esto mueve algo:** entre los seis dados de baja están **Cañitas y Palermo Hollywood**, dos de
las tres subzonas del nudo de Palermo. **Palermo Soho sí sigue.** También se cayeron Microcentro,
Jujuy, Murillo y Nazca; se sumó Lavalle.

**Dos delimitaciones que veníamos usando mal** (informe 437, mayo de 2010):

    Mataderos  usábamos Alberdi 5401-6199     · vigente Av. Alberdi 5501-6299
    Liniers    usábamos Rivadavia 10801-11699 · vigente Ramón Falcón 6801-7299

---

## Lo que espera decisión

1. **Repreguntar las 71 con la compuerta puesta.** Cuesta lo mismo que la ronda 8.
2. **Palermo opción A**: el padre está verificado. Falta nombrar la pieza de 40 ha / 134 locales.
3. **Construir los 80 tramos del IDECBA como geometría** — habilita el cruce real y es lo que más
   rinde ahora.
4. **Colegiales**: la franja de la fuente da tres cuadras. El Polo Concepción sale de Z43 y se
   decide con Palermo.
5. **Las Cañitas**: la ronda de vigencia sigue sin correr, y **el IDECBA no la ayuda**: Cañitas
   fue dada de baja del universo de ejes y no tiene dato vigente (ver abajo).
6. **`LAMINAS_v2_2026-08-08.md` es la vigente.** La v1 quedó marcada como superada en
   `evidencia_2026/INDICE_DE_VERSIONES.md`, con qué cambió y por qué — no se borró.
7. Siguen de antes los pendientes de las rondas 3 a 9.
