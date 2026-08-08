# HANDOFF · Ronda 9 · Places no decía de quién hablaba · 2026-08-08

Continúa `HANDOFF_POLOS_RONDA_8_2026_08_08.md`. Rama `mercados-gastronomicos-v2`.
**Google Places: 8 requests** (4 de la escalera + 4 de la relectura con `displayName`).

## Lo primero: faltan diez archivos

Los siete de **ev21** y los tres de **ev22** que Diego describe **no están en el repositorio**.
Verificado con `find` sobre todo el árbol:

    LA_CORRECCION_DEL_NEW_BRIGHTON.md · COLEGIALES_NO_ES_UNA_COSA.md · errata_2026-08-08.csv
    places_calibracion_releida.csv · places_escalera_de_calibracion.csv
    fuentes_con_defecto_FD20_FD22.csv · colegiales_delimitacion_propuesta.csv
    EL_NUDO_DE_PALERMO.md · EL_ERROR_QUE_SE_REPITE.md · palermo_delimitacion_propuesta.csv

Todo lo que se hizo salió del contenido de los mensajes y de lo que ya estaba en disco. **FD-21 y
FD-22 no se cargaron** por eso, y no se inventaron.

---

## El resultado que cambia el programa de vigencia

La escalera preguntó por cuatro cierres de antigüedad conocida. La hipótesis escrita antes decía
*«Places sigue el lugar, no el negocio»*, y que si La Perla del Once volvía `OPERATIONAL` había
que reescribir v2b.

Volvió `OPERATIONAL`. **Y no es eso lo que pasó.**

| se preguntó por | días | Places devolvió | estado |
|---|---|---|---|
| El Palacio de la Papa Frita | 159 | «El Palacio de la Papa Frita» | `OPERATIONAL` |
| Mercado de los Carruajes | ~480 | «Mercado de los Carruajes» | `CLOSED_PERMANENTLY` |
| Confitería del Hotel Castelar | ~2.290 | **«EX Hotel Castelar.»** | `OPERATIONAL` |
| La Perla del Once | 3.493 | **«La Americana, La Reina de las Empanadas»** | `OPERATIONAL` |

Places no le puso `OPERATIONAL` a La Perla del Once. **Se lo puso a otro establecimiento** —el que
ocupa hoy el local— y lo íbamos a leer como si hablara del bar histórico.

> **El defecto no está en la semántica de `businessStatus`. Está en la ATRIBUCIÓN.** Text Search
> resuelve al lugar que mejor matchea el texto y la dirección le gana al nombre. Sin
> `displayName` en la máscara no se sabe de qué establecimiento habla la respuesta.

**La máscara de la ronda 8 no traía `displayName`.** Sus 70 `OPERATIONAL` no sólo no acreditan
apertura —eso ya estaba escrito— sino que **no se sabe a quién describen**. Su único
`CLOSED_PERMANENTLY` tampoco: puede ser el Plaza Bar o el hotel vacío que lo contiene.

**Y la respuesta no es estable.** La misma `textQuery`, dos minutos después y cambiando sólo la
máscara, devolvió otro lugar para Av. Rivadavia 2800: primero «Av. Jujuy 36», después «Av.
Rivadavia 2800 · La Americana». Con `maxResultCount: 1` se toma el primero de una lista rankeada
que cambia entre llamadas.

La escala corregida está en `outputs/BARRIDO_CIUDAD_2026-08/ronda_9/ESCALA_DE_VIGENCIA_v2c.md`.
Repreguntar las 71 con `displayName` cuesta lo mismo (el campo es Essentials y la máscara ya cae
en Enterprise). **No se ejecutó: espera decisión.**

---

## The New Brighton, corregido

`H084` pasa de `no` a **`en_riesgo`**, misma categoría que `H057` Esquina Homero Manzi. La quiebra
va a tres campos nuevos —`alerta_juridica`, `alerta_juridica_fecha`, `alerta_juridica_fuente`— que
**no tocan el veredicto de vigencia**: la quiebra es un hecho de la sociedad que explota el local,
no del salón.

El catálogo de auditoría pasa de **tres cerrados a dos**; el de `en_riesgo`, de uno a dos.

---

## Dos anclajes de geometría que estaban mal, y el mecanismo es el mismo

### La cola de R20 no era «Cabildo–Balbín»

El callejero oficial guarda el corredor bajo **dos nombres**: `GARCIA DEL RIO AV.` (1.617 m, cruza
Av. Cabildo) y `GARCIA DEL RIO` (1.631 m, cruza Av. Balbín). Se empalman en Pinto.

La ronda 8 buscó sólo el segundo, le pidió el cruce con Cabildo —que está en la otra mitad— y
`tramo_entre` cayó en `nearest_points`: ancló el extremo oeste **761 m fuera del eje** y devolvió
974 m sin avisar. Ese tramo es **Pinto–Balbín**, no Cabildo–Balbín.

|  | ha | locales |
|---|---|---|
| R20 publicada | 61,0 | 102 |
| cola declarada por la r8 | 24,75 (41 %) | 54 (53 %) |
| **cola con el tramo verificado** | **28,63 (47 %)** | **31 (30 %)** |

**El 53 % que Diego citó sale del anclaje mal puesto.** Las calles de la cola corregida están en
`ronda_9/cola_de_R20_calles.csv` — 22 ejes, encabezados por Manzanares, García del Río, Paroissien
y Balbín. El reparto se hizo **por eje más cercano**, no por texto de dirección: el 46,6 % del
universo núcleo no tiene `direccion_norm`.

### La franja de Colegiales es una cuña, no una banda

- **(a) R13** · las cuatro calles son mayoritariamente de Colegiales, pero **Zabala y Conde
  también corren por Belgrano** (918 y 1.165 m) y Zabala además por Chacarita (737 m). Delgado y
  Virrey Avilés son enteramente de Colegiales.
- **(b) R12** · **Av. Álvarez Thomas y Av. Forest se encuentran** —distancia 0 m—: no encierran
  una banda, encierran una cuña. Sólo Zabala (254 m) y Virrey Avilés (344 m) la cruzan con tramo
  verificable: **tres cuadras**, no diez. Delgado queda a 55 m de Álvarez Thomas y Conde a 178 m.
- **(c)** · el tramo de Concepción Arenal entre Zapiola y Conesa mide **143 m** y cae **100 % en
  Colegiales** según la capa de barrios — pero el **47 % de su área a 150 m está dentro de R01
  Palermo**. Dos objetos distintos dan dos respuestas distintas, y hay que decir cuál se usa.
- **control gratis** · Fraga mide 1.492 m en Colegiales ∪ Chacarita ≈ 15 cuadras, con 16 locales
  con la puerta sobre ella. Coincide con Forbes 20/10/2024.

**La ficha sigue sin publicar 495,8 ha ni 891 locales.** Esa medición usa Colegiales a escala de
barrio, que es un techo declarado.

### El cortador nuevo

`tramo_verificado()` distingue **cruza** / **empalma en T** (dentro de 40 m, el caso normal de una
avenida de borde) / **no llega** (y dice a cuánto quedó). El viejo devolvía «1.555 m ≈ 16 cuadras»
para un tramo cuyo corte estaba a 55 m: lo que devolvía era la calle entera.

**Pendiente:** Z23 Flores se verificó y **está bien** (los dos cortes cruzan). Ningún otro uso de
`tramo_entre` se auditó.

---

## Palermo · las tres predicciones fallan

|  | predicho | medido |
|---|---|---|
| R01 ∩ (Soho ∪ Hollywood) | «casi toda» | **43,9 %** de la superficie · 70,7 % de los locales |
| R01 ∩ Las Cañitas | **≈ 0** | **43,65 ha · 210 locales** |
| residuo | 9 locales, un borde | **398 locales, 7 piezas** |

Diego escribió que si (b) daba distinto de cero la hipótesis se caía. **Da distinto de cero.**

**De dónde salía el delta 9:** 407 locales de Soho ∪ Hollywood caen fuera de R01 y 398 de R01 no
están en Soho ∪ Hollywood. 407 − 398 = 9. No era un residuo de borde: era la resta de dos flujos
de cuatrocientos que casi se cancelan. La igualdad de los totales no es evidencia de identidad
espacial.

La contención sí da 0,0 m² perdidos en las cuatro, así que **un polo padre es construible** —pero
por decisión editorial, no porque R01 ya sea sus partes.

---

## Las tres devoluciones

**a) R08 y R21** son **Villa Crespo** (335,5 ha · 823 locales) y **La Paternal** (385,3 ha · 307).
Ninguna es del entorno de Palermo: R08 está a 6 m de R01 y no lo toca. El solape de 49,7 ha está
sobre el contacto Villa Crespo–La Paternal. **Son dos problemas separados.**

**b) La capa FD tenía 9, no «5 + 4 = FD-01..FD-09».** Los cinco previos eran FD-01, 02, 03, 04 y
**FD-12**. Faltaban **diez**, no seis: FD-05..FD-11 y FD-13..FD-15. Se cargaron los diez desde los
CSV de cowork, más **FD-20** con la evidencia de la ronda 8. La capa pasa de 9 a **20**.

**c) El volcado** está en `ronda_9/capa_de_hitos_volcado.csv` — 225 hitos × 21 columnas. Contra
él, los tres casos que motivaron el pedido: **Monserrat tiene 2 Bares Notables en la capa** (H015
Bar Seddon, H094 Bar Iberia), no cinco; El Puentecito es `ICO-004` y Los Campeones `DIR-014`, los
dos ya cargados.

**PGR_P004 · Villa Lugano NO es una baja.** Sigue abriendo por la **vía A**, geométrica y medida
sobre su propio polígono (132 locales en 144 ha, entra en los cortes 25/50/75 %). Pero pasa de dos
vías a una. **Arrastre pendiente:** `seis_vias_94_filas_r8.csv` todavía trae `via_C_abierta = si`.

---

## El método

Cargados en `agent_skills/shared/datagastro_metodo_experimental.md`: **la pregunta cero**, **R14**
(una clase que no estaba en el diseño es sospecha de instrumento) y el **corolario de R6** sin
numerar. Y la estructura de tres familias: R1–R8 el número, R9–R13 el objeto, R14 + pregunta cero
de qué se está hablando.

---

## Lo que espera decisión

1. **Repreguntar las 71 de la ronda 8 con `displayName`.** Sin eso, esa corrida no está atribuida.
2. **Qué cola de R20 se publica** — la de 41/53 % está mal anclada; la verificada da 47/30 %.
3. **Colegiales**: la franja de la fuente da tres cuadras, no diez. Delimitar Z43 con eso o
   aceptar el techo de barrio.
4. **Palermo**: la hipótesis se cayó, pero el polo padre es construible por decisión editorial.
5. **FD-21 y FD-22** siguen sin cargar: falta el archivo.
6. **Las Cañitas** · ronda de vigencia chica, pedida y no ejecutada. La única fuente que delimita
   la zona es de febrero de 2022 y la base le asigna 361 locales.
7. Siguen de antes los pendientes de las rondas 3 a 8.
