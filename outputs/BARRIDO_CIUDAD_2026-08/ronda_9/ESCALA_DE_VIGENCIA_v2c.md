# La escala de vigencia, corregida · v2c

*Ronda 9 · 8 de agosto de 2026 · reemplaza la lectura de `PLACES_PARA_VIGENCIA.md` en todo lo
que se refiere a Google Places.*

Esto se escribe **antes** de que alguien lea los 70 `OPERATIONAL` de la ronda 8 como 70
confirmaciones. No son ninguna confirmación, y ahora sabemos que son menos que eso.

---

## Lo que ya estaba escrito, y sigue valiendo

> **v2b acredita cierre cuando Places lo afirma, y NO acredita nada cuando calla.**

La ronda 8 lo midió sobre tres cierres conocidos: Places marcó uno. Un `OPERATIONAL` es
compatible con un local cerrado hace nueve meses, y con uno con quiebra decretada hace cinco.

**Los 70 `OPERATIONAL` de la ronda 8 confirman CERO aperturas.** Ninguno movió un veredicto
hacia arriba, y la asimetría estaba declarada de antemano.

---

## Lo que la escalera de la ronda 9 agregó, y es peor

Cuatro consultas más, y una relectura de las mismas cuatro con `displayName` en la máscara.

| establecimiento | días | Places dice | y de QUIÉN lo dice |
|---|---|---|---|
| El Palacio de la Papa Frita | 159 | `OPERATIONAL` | «El Palacio de la Papa Frita» |
| Mercado de los Carruajes | ~480 | `CLOSED_PERMANENTLY` | «Mercado de los Carruajes» |
| Confitería del Hotel Castelar | ~2.290 | `OPERATIONAL` | **«EX Hotel Castelar.»** |
| La Perla del Once | 3.493 | `OPERATIONAL` | **«La Americana, La Reina de las Empanadas»** |

### El defecto no está donde lo buscábamos

La hipótesis escrita antes de correr decía: *Places sigue el lugar, no el negocio*. Si La Perla
del Once volvía `OPERATIONAL`, `CLOSED_PERMANENTLY` dejaba de acreditar cierre.

**Volvió `OPERATIONAL`, y sin embargo no es eso lo que pasó.** Places no le puso `OPERATIONAL` a
La Perla del Once: le puso `OPERATIONAL` a **otro establecimiento**, el que ocupa hoy el local. La
respuesta era correcta sobre La Americana y nosotros la íbamos a leer como si hablara del bar
histórico.

> **El defecto no está en la semántica de `businessStatus`. Está en la ATRIBUCIÓN.**
>
> Text Search resuelve la consulta al lugar que mejor matchea el texto, y la dirección le gana al
> nombre. Sin `displayName` en la máscara **no hay forma de saber de qué establecimiento habla la
> respuesta**.

### Y la respuesta no es estable

La misma `textQuery`, con **dos minutos** de diferencia y cambiando sólo la máscara de campos,
devolvió dos lugares distintos para Av. Rivadavia 2800:

    21:28:30   Av. Jujuy 36            OPERATIONAL   (sin displayName)
    21:30:42   Av. Rivadavia 2800      OPERATIONAL   «La Americana»

Con `maxResultCount: 1` se está tomando el **primero de una lista rankeada que cambia entre
llamadas**. Para una pregunta de conteo eso ya se sabía. Para una pregunta de identidad, uno solo
no alcanza.

---

## La regla, v2c

> **Un veredicto de Places sólo se atribuye a un establecimiento si `displayName` corresponde a
> ese establecimiento.** Sin el nombre en la máscara, la respuesta no es sobre nadie en
> particular.
>
> Con el nombre verificado:
>
> - `CLOSED_PERMANENTLY` **acredita cierre**. Es una afirmación positiva sobre una entidad
>   nombrada y es difícil de producir por error. El Mercado de los Carruajes volvió con su propio
>   nombre y su propio cierre: eso vale.
> - `OPERATIONAL` **no acredita nada**. Ni apertura, ni continuidad, ni descarta cierre. El piso
>   de detección medido está por encima de los **2.290 días** —el Castelar—, y ni siquiera es un
>   piso limpio: Places le da `OPERATIONAL` a una ficha cuyo propio nombre empieza con «EX».

### Lo que esto le hace a las corridas ya pagadas

**Las 71 de la ronda 8 salieron sin `displayName`.** Sus 70 `OPERATIONAL` no sólo no acreditan
apertura —eso ya estaba escrito— sino que **no se sabe a qué establecimiento se refieren**. Es
R13 aplicado a la corrida entera, y no se arregla releyendo la tabla: hay que volver a preguntar
con el nombre en la máscara.

El único `CLOSED_PERMANENTLY` de esa corrida —Plaza Bar— **tampoco está atribuido**. Puede ser el
bar histórico o puede ser el hotel vacío que lo contiene. Como el veredicto de la capa ya era
`cerrado_con_reapertura_anunciada` por evidencia documental propia, nada se cae; pero el respaldo
de Places no cuenta hasta que se repregunte.

**Costo de repreguntar:** `displayName` es campo Essentials y **no sube el SKU** —la máscara ya
cae en Enterprise por `regularOpeningHours`—, así que 71 requests vuelven a costar lo mismo que
costaron. No se ejecuta sin decisión de Diego.

---

## La escala, como queda

| nivel | qué es | qué acredita |
|---|---|---|
| v1 | mención sin fecha | nada |
| v2 | hecho fechado de fuente secundaria | trayectoria, no vigencia |
| **v2c** | **Places con `displayName` verificado** | **`CLOSED_PERMANENTLY` acredita cierre; `OPERATIONAL` no acredita nada** |
| v3 | reseña o cobertura fechada con reporteo propio | atención en esa fecha |
| v4 | ficha oficial con edición reciente y horarios propios | atención en esa fecha |
| v5 | sede nombrada por el organizador en una edición fechada | atención en esa fecha |

**`alerta_juridica` no es un nivel de esta escala.** Es un campo aparte, y a propósito: la quiebra
es un hecho de la sociedad que explota el local, no del salón. The New Brighton opera con quiebra
decretada desde el 18/03/2026 y su veredicto de vigencia es `en_riesgo`, no `no`.
