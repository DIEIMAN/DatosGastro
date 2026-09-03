# HANDOFF · Ronda 12 · El catálogo cerrado, la vía C por centralidad, y la lámina que se cayó · 2026-08-08

Continúa `HANDOFF_POLOS_RONDA_11_2026_08_08.md`. Rama `mercados-gastronomicos-v2`.
**Google Places: 0 requests.**

Llegaron los cinco archivos: `EL_CATALOGO_CERRADO.md`, `catalogo_90_estado_final.csv`,
`errata_2026-08-08_ronda_10.csv`, y los dos de ev28 que faltaban —`catalogo_pendientes_para_diego.csv`
y `tanda_1_y_2_para_diego.csv`—, que llegan ya resueltos por el cierre del catálogo.

---

## 1 · El catálogo está cargado. 90 de 90, y la capa quedó cerrada

`hitos/hitos_capa_2026_r11.csv` · diff en `ronda_12/carga_catalogo_90_diff.csv`.

El emparejamiento se hizo **por dirección** (calle + altura), no por nombre: 87 de 90 salen
exactos y los tres restantes son variantes de la misma dirección —*Benito Pérez Galdós 207/201*,
*Esquiú/Esquiu 1393*, *Neuquén esq. Espinosa / Neuquén 1100*—. Por nombre habrían fallado 22.

| | antes | ahora |
|---|---:|---:|
| `sin_verificar` | 53 | **0** |
| `si` | 26 | **87** |
| `en_riesgo` | 2 | 1 |
| `no` | 1 | 2 |
| dudosa / probablemente / señalado / cerrado con reapertura | 9 | 0 |

**62 filas cambiaron de veredicto.**

### El nivel v2/v3 sin fecha entró como tal, y bloquea la cita

Se agregó la columna **`citable_en_documento`**. Las filas resueltas por verificación humana
directa quedan con `vigencia_nivel = "v2/v3 sin fecha individual"` y **`citable_en_documento =
False`**: resuelven la fila, no se citan. **58 filas no citables, 32 citables con fecha propia.**

### Tres precisiones que salieron al cargar

**Son 52 filas firmadas por vos, no 54.** De ellas 51 estaban sin verificar y una —*Los Galgos*—
ya estaba en `si`. Las otras dos resoluciones del día vinieron del relevamiento documental. El
cierre en 90 de 90 no se mueve.

**El bar 91 de la capa es `H064 La Esquina de Aníbal Troilo`** (Paraguay 1500), que no está en los
90 y queda en `senalado_no_cerrado` — el único sin resolver de todo el relevamiento patrimonial,
tal como decía tu ficha.

**Plaza Asturias y El Globo no están en la capa.** No es que les falte la fecha: **no existen como
hitos.** Y El Globo no figura en ningún registro oficial, así que la lámina 5 —*«4 establecimientos
reconocidos en 1.100 m²»*— no puede llamar «reconocidos» a los cuatro. Quedó marcada como no
citable hasta cargarlos y verificarlos.

---

## 2 · Decisión n.º 23 · aplicada, y ninguna de las dos se cae

Registrada en `ronda_11/decisiones_tomadas_2026-08-08.csv`. Detalle en
`ronda_12/decision_23_aplicada.csv`.

**Las dos verificaciones que pediste, antes de tocar nada:**

| | R07 Costanera Norte | PG009_COSTANERA_NORTE |
|---|---|---|
| A · densidad | **sí** (polo P001) | **sí** |
| B · trayectoria | pendiente · 1 hito sin verificar (Happening) | heredada de R07 |
| C · centralidades | ~~sí~~ → **no** | ~~sí~~ → **no** |
| D · comunidades | no | heredada · no |
| E · reconocimiento | no · quedó a un grupo del umbral | heredada · no |
| F · corredor | **sí** · elongación 8,06, la más alta de las 22 | **sí** |

> **(a) R07 sigue abriendo por A y F. No se da de baja, y no necesita el argumento de excepción:
> se sostiene por densidad y por forma.** La ficha lo declara así.
>
> **(b) PG009 también sigue abriendo por A y F. No se cae. No hay baja que argumentar.**

Vía C abierta: **22 zonas de 4 a 3 · 94 filas de 3 a 2.** Salidas en
`seis_vias/seis_vias_22_zonas_r12.csv` y `seis_vias/seis_vias_94_filas_r12.csv`.

Bonpland, Belgrano y del Progreso mantienen. Con el criterio nuevo, del Progreso se salva por la
prueba directa —organiza Caballito— y no por la segunda mitad de una conjunción, que es más
robusto.

---

## 3 · El IDECBA · lo que pediste era corregir un conteo, y se cayó una lámina

`ronda_12/idecba_48_autoridad.csv` · `idecba_los_6_que_salen.csv` · `idecba_pruebas_laminas_14_15.csv`

Tenías razón: **son 48 ejes vigentes y la autoridad es el XLSX.** El cruce da 47 en común, seis
que salen y uno que entra.

    SALEN:  Microcentro · Palermo Hollywood · Cañitas · Nazca · Murillo · Jujuy
    ENTRA:  Lavalle  (Corrientes 501-999 · Lavalle 501-999 · Esmeralda 401-599)

### El problema es cuál salió

> **«Microcentro» no está entre los 48.** El 63,2 % de ocupación y la caída de 7,2 puntos —que
> sostenían **la lámina 14 entera**, la primera fila de la 15, el remate de `EL_CATALOGO_CERRADO.md`
> y la recomendación *«si hace falta una sola lámina, la 14»*— **no existen en la serie vigente.**

Los cuatro cuatrimestres del XLSX —1.º de 2025 al 1.º de 2026— traen los mismos 48 ejes y ninguno
incluye Microcentro. **No era un valor viejo: era otro universo.**

**Cambiar «53» por «48» habría dejado la lámina en pie con un número que no existe.** Las láminas
14 y 15 se rehicieron de cero.

### Y con la planilla como autoridad se cayeron dos afirmaciones más

| afirmación de la v2 | medida sobre los 48 | veredicto |
|---|---|---|
| «los polos consagrados son los que más comercio pierden» | polos **−1,69 pp** (n=21) · no polos **−1,30 pp** (n=21) | **REFUTADA** · 0,39 pp no es una brecha |
| «la brecha no es entre el norte y el sur» | Norte **0 de 9** ejes suben, media −2,39 · Sur **7 de 13**, media **+0,48** | **REFUTADA, y al revés** |
| «el eje más vacío tiene sus doce notables abiertos» | el eje con más notables adentro tiene **3** | no se sostiene como estaba |
| «la media de la Ciudad es 90,1 %» | **90,0 %**, 12.896 relevados (no 15.636) | se sostiene; el volumen no |

Dos casos concretos que la v2 citaba al revés: **Defensa sube 2,7 puntos** (decía −5,4) y
**Liniers no se movió** (decía −4,6, y era el remate de la lámina 4).

### Lo que sí quedó, y es mejor que lo que había

Con los **80 tramos del glosario** —calle y rango de alturas— se pudo atribuir el padrón por
dirección en vez de por nombre de eje: `ronda_12/notables_90_x_eje_idecba.csv`.

> **De los 90 Bares Notables, 18 caen adentro de un eje que la Ciudad releva a pie.
> 17 abiertos, 1 en riesgo, 0 cerrados — mientras esos 48 ejes pierden 1,6 puntos de ocupación.**

Es la afirmación que querías para la segunda mitad de la lámina 14, ahora con denominador de los
dos lados. Y la salvedad se volvió más estricta: **ninguno de los tres casos graves cae adentro de
un eje relevado.** Plaza Bar está en Florida **1005** y el eje Florida termina en el **999** —seis
números afuera—; The New Brighton y el Hotel Castelar no están sobre ninguna calle relevada.

### Una pata de Palermo que se cae

La serie vigente releva **un solo eje de Palermo: Soho.** El argumento de que *«la Ciudad ya
delimita Soho, Hollywood y Cañitas como tres cosas»* **se apoyaba en los dos que salieron.**
Chacarita y Colegiales sí siguen como ejes distintos.

### Y el aviso ya estaba escrito

`INDICE_DE_VERSIONES.md` registraba esta salvedad **desde la ronda 10**, con los seis ejes
nombrados. Las láminas se armaron igual con los números del PDF. **Registrar el defecto en un
índice no lo corrige si no llega al documento que circula.**

---

## 4 · Errata cargada · `ronda_12/errata_ronda_10_aplicada.csv`

ERR-01 y ERR-02 aplicadas con alcance mayor al pedido (arriba). ERR-05 es la lámina 10, reescrita.
ERR-03 y ERR-04 **ya estaban aplicadas en la ronda 11**: la ronda 11 hizo el cruce contra
`DECISIONES_TOMADAS` antes de cargar, que es justamente lo que faltaba en la quinta aparición de R9.

Documentos tocados: `LAMINAS_v2_2026-08-08.md` (ahora **v2.1**, láminas 4, 5, 10, 12, 14, 15 y las
notas de cierre), `LA_FUENTE_QUE_NOS_FALTABA.md`, `EL_CATALOGO_CERRADO.md`,
`INDICE_DE_VERSIONES.md`, y las dos tablas del IDECBA reescritas sobre los 48.

---

## Lo que espera decisión

1. **Plaza Asturias y El Globo**: cargarlos como hitos y verificarlos con fecha. **Bloquea la
   lámina 5**, que hoy no se puede usar.
2. **La lámina 14 rehecha**: leerla y decir si el par —48 ejes perdiendo 1,6 puntos / 18 notables
   adentro, todos operando— reemplaza bien al 63,2 %. Es más honesta y menos impactante.
3. **Repreguntar las 71 de Places con la compuerta puesta** (viene de la ronda 10).
4. **Construir los 80 tramos como geometría.** Con la atribución por calle + altura ya funcionando,
   lo que agrega la geometría es resolver los cruces y las esquinas.
5. **Palermo opción A**: falta nombrar la pieza de 40 ha / 134 locales. Y ahora sin la pata del
   IDECBA.
6. Siguen de antes los pendientes de las rondas 3 a 11.
