# HANDOFF · Ronda 11 · Dos decisiones nuevas y el barrido de la vía C · 2026-08-08

Continúa `HANDOFF_POLOS_RONDA_10_2026_08_08.md`. Rama `mercados-gastronomicos-v2`.
**Google Places: 0 requests.**

Los dos archivos de ev28 —`catalogo_pendientes_para_diego.csv` y `tanda_1_y_2_para_diego.csv`—
**no llegaron al repositorio**. Las cuatro decisiones venían completas en el mensaje, así que se
aplicaron igual.

---

## 1 · De las cuatro decisiones, dos ya estaban tomadas

R9 sobre el propio catálogo de decisiones, antes de cargar nada:

| | decisión | estado |
|---|---|---|
| **(a)** | Untappd = v3b | **ya registrada** como n.º 3 (07/08) |
| **(b)** | reporteo a nivel programa = v4 | **ya registrada** como n.º 2 (07/08) |
| **(c)** | centralidad privada y planificada no abre vía C | **nueva** → n.º 21 |
| **(d)** | R22 se publica con la debilidad declarada | **nueva** → n.º 22 |

**Y las tres aplicaciones ya estaban hechas en la capa:**

    H069  LA PERLA       verificado_abierto  v3b  Untappd, check-ins del 20 y 17/05/2026
    ICO-015 Tancat       verificado_abierto  v2   Instagram @tancattasca, verificado por Diego
    ICO-002 El Imparcial probablemente_abierto v4 Info Gastronómica 07/07/2026 (programa)

**Una precisión sobre (b):** *«Tancat y El Imparcial… siguen probablemente_abierto»* no es exacto.
**Tancat queda en `verificado_abierto`**: bajó a v4 por el reporteo de programa, pero conserva el
veredicto por el **v2 de Instagram que verificaste vos el 07/08**. Está escrito así en la
consecuencia de la decisión n.º 2. El que queda en `probablemente_abierto` es **El Imparcial** solo.

---

## 2 · El barrido de la vía C · ninguna fila la pierde, y una queda para vos

**La capa de hitos no tenía con qué decidir:** `registro_oficial` está vacío en los once
`Mercado/patio` y no existe campo de titularidad ni de gestión.

**El dato sí existe, relevado:** `outputs/mercados_caba/sanitized/mercados_gastronomicos_activos_v4.csv`
trae `tipo_primario` y `gestion` para los trece del subproyecto Mercados. Se leyó de ahí en vez de
clasificar de memoria — R13.

**Quedan 3 filas de las 94 y 4 zonas de las 22 con vía C abierta** (eran 4 y 4 antes del retipado
de Yiyo el Zeneize):

| quién | abre con | tipo | gestión | veredicto |
|---|---|---|---|---|
| Palermo Hollywood · R01 Palermo | Mercado Bonpland | mercado_de_productores | mixta | **mantiene** |
| R05 Belgrano | Mercado de Belgrano | mercado_histórico | mixta | **mantiene** |
| Caballito · R10 | Mercado del Progreso | mercado_barrial_alimentario | **privada** | **mantiene** |
| **Costanera Norte · R07** | **Patio Costanera Norte** | **patio_gastronómico** | **mixta** | **para vos** |

**Ninguna pierde la vía C automáticamente.**

### El caso que no cierro yo

**Patio Costanera Norte** es lo único que queda. Tu criterio dice «privada **y** planificada», y el
relevamiento lo tipifica como **patio gastronómico de gestión mixta**: es planificado y **no** es
privado.

- **Por la letra**, mantiene la vía C.
- **Por el espíritu** —una centralidad comercial construida como desarrollo— es exactamente el caso
  que quisiste excluir.

Elegir una de las dos lecturas es *tomar* tu decisión, no aplicarla. Si la definís, se aplica en
una corrida: afecta a `PG009_COSTANERA_NORTE` en las 94 y a `R07` en las 22.

### El caso que sorprende, y confirma que las dos condiciones hacen falta

**El Mercado del Progreso es de gestión privada.** Pero no es planificado —1889, abasto de barrio—,
así que mantiene la vía C sin ambigüedad. Si el criterio hubiera sido «privada» a secas, R10
Caballito habría perdido una vía por un mercado de 137 años.

---

## 3 · R22 Villa Pueyrredón · el 5,6 % verificado, y su curva

`PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN` — 198 locales · 305,55 ha · **una sola vía abierta**
(A). C y F cerradas; B, D y E se heredan de la zona R22.

**El 5,6 % es correcto y es el umbral de 40 m.** La continuidad depende del umbral, así que va la
curva (R4):

| umbral | 20 m | 40 m | 60 m | 80 m | 120 m |
|---|---|---|---|---|---|
| continuidad | 2,5 % | **5,6 %** | 11,6 % | 15,7 % | 31,3 % |

Densidad 0,648 locales/ha · vecino medio 36,2 m.

Citar sólo el 5,6 % no es incorrecto, pero **la ficha gana con la curva**: a 120 m la continuidad
es del 31,3 %, y esa diferencia es justamente lo que hace discutible a la fila. El texto propuesto
está en `ronda_11/R22_ficha_debilidad_declarada.csv` y ya incluye los dos extremos.

---

## 4 · El IDECBA ya está bajado

`AC_EJ_2026_03.xlsx` y `AC_EJ_48_GLOS.xlsx` se bajaron en la **ronda 10** y están procesados:

- `ronda_10/idecba_densidad_48_ejes.csv` — **locales relevados, cuadras y densidad comercial** por
  eje. Es lo que pedís para comparar contra la vía A.
- `ronda_10/idecba_serie_48_ejes.csv` — los cuatro cuatrimestres y la variación interanual.
- crudos en `outputs/BARRIDO_CIUDAD_2026-08/idecba/crudos/`.

**Son 48 ejes vigentes, no 53.** Las cuadras no vienen como columna: se derivan de
`relevados ÷ densidad` y el cociente cierra contra el total declarado (13,81 locales por cuadra).

**Y la comparación con la vía A no es directa:** el IDECBA mide locales por **cuadra** sobre un eje
lineal y la vía A mide locales por **hectárea** sobre un polígono. Habilita calibración, no
equivalencia.

---

## Lo que espera decisión

1. **Patio Costanera Norte**: ¿«mixta» cae del lado de privada o no? Afecta PG009 y R07.
2. **Repreguntar las 71 de Places con la compuerta puesta** (viene de la ronda 10).
3. **Construir los 80 tramos del glosario del IDECBA como geometría** — sigue siendo lo que más
   rinde: convierte el cruce nominal (27 de 48) en atribución real.
4. **Palermo opción A**: falta nombrar la pieza de 40 ha / 134 locales.
5. Siguen de antes los pendientes de las rondas 3 a 10.
