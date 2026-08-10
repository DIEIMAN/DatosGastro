# La ronda 15 de Codex, verificada contra disco

**10 de agosto de 2026** · leído en `ronda_15_codex/` y en `criterio_admision_55.csv`

---

## Lo que está bien, y está muy bien

**El reparto se midió con la disciplina correcta.** Universo ERR-10 reproducido en 23.981 registros,
superficies en EPSG:5347, **contención verificada por superficie perdida y no con `covers()`** —la
regla que costó una errata en su momento—, y **una columna que declara de qué archivo sale cada
geometría.** Esa última columna es la que permitió encontrar lo único que hay para observar, así
que conviene decirlo: **el hallazgo de abajo existe porque Codex declaró sus soportes.**

**Iriarte queda separada, y con margen amplio.** Contra Montes de Oca y contra Boulevard Caseros dio
**0 m² de intersección y 0 locales compartidos en las dos direcciones.** No es un caso ajustado: son
objetos disjuntos. Los dos cotejos se hicieron contra geometría real —la concentración medida de
Montes de Oca y el perímetro publicado de Boulevard Caseros—, así que **este resultado se puede
firmar hoy.**

**Y corrige una cifra que este atlas llegó a publicar.** El documento decía que el conjunto podía
cerrar «entre 39 y 41». Medido, **el piso no es 39: es 40**, y sólo si se firma una fusión. Estaba
escrito antes de medirlo y ya está corregido.

---

## Lo único que hay para observar, y no es un error de medición

**La contención de Sáenz dentro de Pompeya se midió contra un polígono provisorio.**

| | superficie | qué es |
|---|---:|---|
| Sáenz · lo contenido | 504.234,53 m² | **la concentración medida P024**, con sus 95 locales |
| Pompeya · el contenedor | 8.700.695,44 m² | **el polígono administrativo del barrio**, 870,07 ha |

**Pompeya es uno de los dieciocho polos que todavía no tienen perímetro propio.** Su geometría en el
repositorio es la del barrio de Nueva Pompeya más Parque Patricios, un provisorio declarado como tal.

Y este atlas ya escribió la regla que aplica acá, en el pie de todos sus mapas y en el documento de
magnitudes: **un cruce espacial contra un polígono de barrio mide el barrio, no el polo.**

> **Que Sáenz esté dentro del barrio de Pompeya no es un hallazgo: es la definición de Sáenz.** El
> Mercado de Pompeya está en Nueva Pompeya. Lo que habría que saber para firmar la fusión es si
> Sáenz está dentro **del polo**, y eso todavía no se puede medir porque el polo no tiene borde.

**La medición es correcta. Lo que se adelanta es la recomendación.** Y tiene arreglo automático:
Pompeya está en la lista de perímetros que se están trazando ahora. Cuando tenga borde propio, la
misma corrida da la respuesta buena.

**Mientras tanto el conteo no se mueve: 41 polos.** Sáenz sigue publicándose como ficha propia, con
la contención declarada adentro.

---

## Villa Soldati queda cerrada, y por dos caminos

**Primero, la fuente pública no la respalda.** Tres recursos oficiales de ferias y mercados —30
ferias especializadas, 184 ubicaciones de feria itinerante y 6 mercados— registran las dos ferias de
Villa Soldati ya conocidas y **ninguna sobre Mariano Acosta**. La afirmación original no traía norma,
permiso ni identificador de fuente.

**Y Codex puso la salvedad correcta sin que nadie se la pidiera:** los padrones tienen fecha de
corte, y **la ausencia de registro no es registro de ausencia.** Queda como puerta cerrada, no como
prueba territorial.

**Segundo, y esto sí concluye.** Aunque mañana apareciera la fuente y la vía abriera, **Villa Soldati
pasaría de cero a una vía**, por debajo del umbral de dos. **La contradicción, por sí sola, no podía
crear un polo en la Comuna 8.**

> Durante semanas esto figuró en el tablero como la única pregunta abierta cuya respuesta cambiaba el
> mapa. **Estaba mal categorizada.** Era importante de contestar y no era decisiva, y **son dos cosas
> distintas.** Vale la pena que quede escrito, porque confundirlas cuesta tiempo.

**Efecto en el documento:** Villa Soldati · Mariano Acosta pasa de *zona en estudio* a *zona evaluada
sin admisión*. Las categorías quedan en **41 · 1 · 3 · 10**.

---

## Lo demás, cotejado

**ERR-18 corregido** y con el resultado esperado: R02=4, R04=4, R05=5, R19=4, Z37=5, y **ninguna fila
cambia de categoría** —que era la prueba de que el error era de registro y no de criterio—.

**ERR-19 corregido**: la fila R03 vuelve a diez campos, con `via_E_rutas_n=6` y la fecha en su
columna.

**ERR-17 cerrado**: el corpus pasa de 48 a 53 filas con Z50–Z54, y **Montes de Oca quedó vinculada a
P066 y a la ronda 14 en vez de duplicarse como «polo 42»**, que era exactamente el riesgo.

---

## Una cosa que no hizo, y está bien que no la haya hecho

**Codex declara que no corrió `git add`, commit ni push.** Correcto: el repositorio está siendo
escrito por otro proceso en paralelo. **Los archivos están en disco y el commit puede esperar** — es
la decisión que este mismo trabajo tomó una hora antes, por la misma razón.
