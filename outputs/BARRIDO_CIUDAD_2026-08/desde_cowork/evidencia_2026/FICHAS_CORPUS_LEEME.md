# El corpus de fichas · 48 zonas, listo para ensamblar

*7 de agosto de 2026 · con las 20 decisiones aplicadas*

`fichas_corpus_polos.csv` reúne, zona por zona, todo el material que necesita una ficha. **No depende de la geometría**: depende de la zona, y el conjunto de zonas ya está cerrado. Cuando el repositorio termine los polígonos, las fichas se ensamblan en vez de escribirse.

---

## El conjunto de polos, después de las 20 decisiones

| | cuántos |
|---|---|
| **Referencias publicadas** (R18 absorbida en Retiro) | **21** — de las cuales 3 se amplían |
| **Zonas nuevas que entran** | **15** |
| **Total publicable** | **36 polos** |
| Pendientes de una decisión o de un conteo | 5 |
| Descartadas, con el descarte argumentado vía por vía | 7 |

Las tres que se amplían son R19 Federico Lacroze, R20 García del Río y R21 La Paternal. La que se absorbe es R18 Esmeralda-Paraguay, dentro de Z46 Retiro.

---

## Qué trae cada fila

Veinticinco campos. Los que importan:

- **`perimetro_textual`** — la delimitación en calles y alturas, tal como la sostienen las fuentes. Es lo que el repositorio va a poligonizar.
- **`anclaje_normativo`** — la norma que respalda el perímetro, cuando existe. La mayoría no tiene, y eso también es un dato.
- **`via_A` a `via_F`** — el estado de cada vía **con las decisiones ya aplicadas**. Donde una vía cambió por una decisión, está marcado.
- **`via_E_texto_publicable`** — el texto de ≤240 caracteres ya redactado para la ficha y la matriz. Está escrito para las 36.
- **`hitos_conocidos`** — cada hito con dirección, registro oficial y estado de vigencia, incluida la fecha de verificación.
- **`alerta_de_vigencia`** — lo que no se puede publicar sin chequear.
- **`nota_de_delimitacion`** — el problema específico de esa zona. Es el campo más largo y el más útil.
- **`decisiones_aplicadas`** — qué números de la lista de 20 tocaron esa fila.
- **`que_falta_para_la_ficha`** — el pendiente concreto.

---

## Lo que las decisiones cambiaron, zona por zona

**Decisión 1 · la FIAB no abre la vía C.** Se cayó la vía C de cinco zonas: Flores casco histórico, Floresta, Monte Castro, Villa Ortúzar y Monserrat. **Ninguna de las cinco cambia de veredicto**, pero cuatro pierden una vía. Y sostiene el cero de Villa Soldati, que con la FIAB computando habría pasado de 0 a 1 y entrado — el resultado absurdo que la decisión evita.

**Decisión 5 · R18 se absorbe en Retiro.** Los cuatro Bares Notables de R18 —Bárbaro, Saint Moritz, Florida Garden y el Plaza Bar— pasan a Z46, que queda con la concentración más alta del Atlas: cuatro notables en seis cuadras. Uno de ellos cerrado desde 2017.

**Decisión 13 · Congreso se fusiona con Monserrat.** Queda un solo polo del eje Av. de Mayo–Callao, anclado en el **Decreto 437/1997**, que declara la avenida Lugar Histórico Nacional. Ese decreto recae sobre el eje mismo y no sobre un polígono de casco: es mejor anclaje para un polo lineal que el APH1.

**Decisión 14 · Flores son tres polos.** El casco histórico queda pendiente de redelimitación, Avellaneda entra con seis grupos y Bajo Flores va con ficha propia.

**Decisión 17 · el enclave coreano se delimita por el clúster.** Cruza tres barrios y tres comunas: Av. Avellaneda 3069 es Flores, Cuenca 954 es Villa Santa Rita, Campana 685 es Floresta. Va a la edición técnica como caso de prueba de la definición.

---

## Y una consecuencia que apareció sola: Café Olimpo cambia de barrio y de zona

El repositorio verificó que el callejero reparte Irigoyen por altura: Villa Luro termina en el 1299 y el 1301–1799 impar es Monte Castro. **Café Olimpo, Irigoyen 1491, está en Monte Castro.**

Eso mueve dos fichas en direcciones opuestas:

- **Z31 Villa Luro pierde su única vía B.** Y por dos motivos separados: el hito no está en el barrio, y aunque lo estuviera queda a 1.532 metros del polígono. Entra igual por A, E y F, pero es ahora el caso más expuesto de los que entran.
- **Z28 Monte Castro se refuerza.** Suma un Bar Notable de 1950 a El Fortín, que ya tenía doble reconocimiento. Sigue pendiente del conteo de continuidad sobre Álvarez Jonte, pero con dos anclas en vez de una.

---

## Lo que este corpus deja al descubierto

**Cinco zonas dependen de un solo hito.** San Telmo (El Federal), Bulevar Caseros (el Británico), Villa Urquiza (Café de la U), La Paternal (MN Santa Inés) y Flores casco histórico (La Farmacia, y encima fuera del polígono). Si ese hito cae, la vía B de la zona cae entera. Es el escenario que ya vimos con P008 y Los Laureles.

**Dos zonas tienen cero hitos y entran igual.** Donado-Holmberg —con cuatro grupos de vía E, el máximo de las 22— y García del Río. Son la mejor prueba de que las vías son alternativas, y a la vez las más frágiles si la prensa envejece.

**Y hay una asimetría llamativa entre las 22 y las nuevas.** Las publicadas tienen polígono y a menudo no tienen hitos verificados; las nuevas tienen hitos verificados esta semana y todavía no tienen polígono. Almagro tiene sus cinco Notables confirmados en siete días. Recoleta tiene seis hitos y ninguno verificado individualmente.

---

## Lo que falta, y no es escritura

Para las 36 fichas ya está el texto de vía E, el perímetro textual, los hitos con dirección y registro, el anclaje normativo cuando existe, las alertas y las notas de delimitación.

Falta:

1. **El polígono** — es del repositorio y arranca ahora con las tareas 3 y 4.
2. **Las cifras de A, C y F por zona** — se recalculan cuando cambien los polígonos, así que tomarlas antes sería trabajo perdido.
3. **Verificar los hitos de las 22 publicadas.** Es el hueco más grande que queda: Recoleta, Puerto Madero, Villa Crespo, Devoto y Caballito tienen hitos sin una sola verificación individual. La pasada de Places los cubre a todos de una vez.
4. **Las fotos, si las hubiera** — ya está decidido que no van.

Ninguno de esos cuatro es redacción. **La fase 3 está lista para ensamblarse en cuanto cierre la 2.**
