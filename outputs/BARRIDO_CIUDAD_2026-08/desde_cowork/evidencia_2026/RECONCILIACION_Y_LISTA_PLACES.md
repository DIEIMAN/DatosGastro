# Más de la mitad de los Bares Notables de la Ciudad queda fuera de las 22

*Reconciliación de hitos · 7 de agosto de 2026*

Al cruzar los hitos de las 22 referencias publicadas contra el catálogo consolidado apareció un número que conviene tener a la vista antes de poligonizar.

---

## El número

El catálogo vigente —anexo de la Res. MCGC 1225/26, "Consolidado 2025"— tiene **90 Bares Notables**.

Sumando los que caen dentro de las envolventes de las 22 referencias: **41**. Y de esos, algunos están contados dos veces, porque R12 Centro y R18 Esmeralda-Paraguay se pisan sobre Saint Moritz y Florida Garden.

**Alrededor de la mitad de los Bares Notables de la Ciudad queda afuera de las 22 envolventes.**

Y no es que estén en barrios que el Atlas no cubre. Están en barrios que el Atlas **sí** cubre, y a veces son el hito principal de la zona:

| establecimiento | dirección | barrio | la referencia que debería contenerlo |
|---|---|---|---|
| Casa Watson | Vuelta de Obligado 2072 | Belgrano | **R05 Belgrano** |
| Varela Varelita | Av. Scalabrini Ortiz 2102 | Palermo | **R01 Palermo** |
| Los cinco de Almagro | Guardia Vieja, Bulnes, Corrientes ×2, Rivadavia | Almagro | R13 Abasto tiene dos de ellos |
| Los nueve de Monserrat | eje Av. de Mayo | Monserrat | R12 Centro tiene algunos |

---

## Los dos casos que lo muestran sin discusión

**R05 Belgrano tiene cero Bares Notables en su envolvente.** Su único hito de vía B es el Mercado de Belgrano. Y Casa Watson, Bar Notable del catálogo, está en Belgrano y verificado abierto con una reseña del 5 de julio.

**R01 Palermo tiene cero Bares Notables en su envolvente**, y no es que Palermo no tenga: tiene Varela Varelita, verificado abierto con reseña del 25 de junio, y Café Cortázar, que es una de las doce altas de agosto. Los veinte hitos que la envolvente sí contiene son **todos Michelin y 50 Best** — distinción de restaurante, que rota mucho más rápido que un Bar Notable y que dice algo distinto sobre la zona.

Es la misma cosa que el repositorio encontró en Almagro: `PGR_P083` mide 5,7 hectáreas y el barrio mide 405. Solo que acá pasa con las envolventes publicadas, que son las curadas.

---

## Y tres referencias tienen cero hitos de cualquier tipo

**R16 Donado-Holmberg, R20 García del Río y R22 Villa Pueyrredón** tienen `via_B_total = 0`.

Las dos primeras entran igual —DoHo con cuatro grupos de vía E, el máximo de las 22— y eso está bien: las vías son alternativas. Pero conviene que la ficha lo diga, porque son las zonas que más dependen de que la prensa no envejezca.

R22 Villa Pueyrredón abre **una sola vía, la A, y con 5,6 % de continuidad**. Es la referencia más débil del conjunto, y queda como decisión tuya si se publica igual por la regla de que las 22 se mantienen.

---

## La lista para Places, ordenada por lo que resuelve

`lista_places_prioridad.csv`, **71 establecimientos en cuatro prioridades**.

### Prioridad 1 · seis hitos únicos sin verificar

Son los que, si caen, se llevan la vía B de una fila entera. Ya vimos ese escenario con P008 y Los Laureles.

- **Café de la U** — único hito de R17, que además es el caso de vía E más frágil de las 22.
- **MN Santa Inés** — único hito de R21, justo cuando la zona se amplía.
- **Británico** — único hito de R11, cuya vía A no abre y cuya vía E es débil por antigüedad.
- **San Bernardo** — único Bar Notable de R08; los otros cinco hitos son Michelin y 50 Best.
- **Esquina Homero Manzi** — **en riesgo**, condena laboral de 220 millones. Hito más visible de R14.
- **Café de García** — uno de los dos de R15, la zona con la cobertura más fresca de las 22 y cero verificación.

### Prioridad 2 · seis que están fuera de la envolvente y ya verificamos

Acá Places no verifica: **confirma la dirección formateada** para que el cruce espacial ubique bien el hito. Casa Watson, Varela Varelita, Café Olimpo, El Tokio, Los Laureles y La Perla de Caminito.

### Prioridad 3 · seis que rinden por partida doble

Tres tocan varias filas a la vez —Saint Moritz, Florida Garden y Bárbaro, que suman tres filas cada uno— y **tres son tests de calibración**. Esa parte importa:

- **Plaza Bar**, cerrado desde abril de 2017 con el edificio en obra. Si Places no lo da cerrado, la herramienta no sirve para lo que la queremos.
- **The New Brighton**, quiebra judicial de hace cinco meses.
- **La Buena Medida**, cerrada hace nueve meses.

**Tres cierres a nueve años, nueve meses y cinco meses.** Donde esté el corte de detección de Places, va a estar ahí. Y con eso sabremos exactamente cuánto vale su `business_status` para nosotros, en vez de suponerlo.

Hay además dos tests de reapertura que valen igual: **El Tokio**, que cerró en 2023 y volvió en 2025, y **Los Laureles**, que cerró hace tres semanas y ya reabrió. Si Places arrastra el cierre viejo de uno y no ve la reapertura del otro, queda confirmada la asimetría que ya escribimos.

### Prioridad 4 · los 53 restantes de las 22

Todos los hitos de referencias publicadas sin ninguna verificación individual: Recoleta entera, Puerto Madero entero, Villa Crespo, los ocho de Corrientes, los seis de Palermo, los del Centro.

---

## Por qué esto cambia el orden del trabajo

Cuando autorizaste Places, el argumento era resolver los tres dudosos que quedaban. Esos tres ya los cerraste vos a mano.

**El uso real es otro y es más grande: verificar de una vez los hitos de las 22 publicadas**, que es el único hueco importante que sigue abierto del lado de los datos. Son 53 establecimientos que nunca fueron mirados, en las zonas que el Atlas presenta como sus polos consolidados.

Y hay una asimetría que conviene decir en voz alta antes de publicar: **las zonas nuevas están mejor verificadas que las viejas.** Almagro tiene sus cinco Notables confirmados en siete días. Recoleta tiene ocho hitos y ninguno mirado. Si el Atlas sale así, la parte más sólida va a ser la que se agregó esta semana.
