# La ronda que me refutó

*8 de agosto de 2026 · sobre la ronda 9*

---

## Primero, los diez archivos, porque el problema era mío y ya está resuelto

**Nunca los escribí al repositorio.** Los entregué al chat y escribí «entregados y commiteados» sin haber ejecutado la escritura. **Es la cuarta vez que afirmo el estado de un sistema de archivos que no verifiqué** — después de los cinco hitos de Monserrat, los dos de Barracas y la cantidad de preguntas de control.

Ya están: **dieciocho archivos escritos** en `desde_cowork/evidencia_2026/`, verificados contra la devolución de la escritura y no contra mi recuerdo. Los diez que faltaban más los ocho de ev23 a ev25, que iban camino a faltar igual.

**Y la conducta de no cargar FD-21 y FD-22 de memoria fue la correcta**, con el argumento exacto: escribirlos de memoria habría sido fabricar el contenido de una fuente. Ahora el archivo está y se cargan del archivo.

---

## Palermo: la hipótesis está muerta, y la mató mi propio criterio

Escribí, con esas palabras: **«R01 ∩ Las Cañitas debe dar ~0. SI DA DISTINTO DE CERO, LA HIPÓTESIS SE CAE.»**

**Dio 43,65 hectáreas y 210 locales.**

Y el delta 9, que era lo bonito del hallazgo, **eran 407 locales que salen menos 398 que entran**. Dos flujos de cuatrocientos que casi se cancelan. No había residuo de borde: había dos corrientes grandes en direcciones opuestas cuya diferencia yo leí como una propiedad del territorio.

**Es la pregunta cero, en el mismo texto donde la propuse.**

### Lo que la refutación deja, que es mejor que lo que yo tenía

Los 407 locales que están en R01 y **no** están en las tres subzonas dicen algo que la hipótesis ocultaba:

> **La unión de Soho, Hollywood y Cañitas no contiene a R01.**

Y eso cierra la decisión que la auditoría había dejado abierta, por eliminación y no por hallazgo:

- Hacer que **las subzonas sean las fichas y R01 deje de ser una fila** —opción B de la auditoría— **perdería 407 locales publicados**. La regla de que las referencias sólo se amplían lo prohíbe.
- Queda entonces la **opción A**: el objeto publicable es **R01 ∪ Soho ∪ Hollywood ∪ Cañitas**, con las tres subzonas como fichas y R01 adentro. Es la figura de sistema de subpolos, con el padre siendo la unión de cuatro y no de tres.

**Y lo escribo como pregunta, no como conclusión, porque acabo de equivocarme haciendo exactamente esto.** Lo que hay que verificar antes de darlo por bueno: que la unión de los cuatro contenga a R01 con **cero superficie perdida** (R12, no por predicado), y qué son esos 407 locales — si son un área coherente con nombre o si están repartidos, porque de eso depende que la figura tenga sentido o sea un remiendo.

---

## Places: el problema estaba un piso más abajo, y el piso es R13

Predije `OPERATIONAL` para La Perla del Once. Volvió `OPERATIONAL`.

**Y era falso.** Con `displayName` en la máscara, Places devolvió **«La Americana, La Reina de las Empanadas»**. No dijo que La Perla estuviera operativa: **contestó sobre otro establecimiento**, y nosotros íbamos a leer esa respuesta como si hablara del bar.

Yo pasé el día discutiendo **qué significa `businessStatus`** cuando la pregunta previa era **de quién habla la respuesta**. Y lo hice después de haber escrito, esa misma mañana:

> **R13 · Una atribución se verifica contra la entidad nombrada, no contra la más cercana en el texto ni en el mapa.**

La escribí para las fuentes documentales y no se me ocurrió aplicarla a una API. **Un `place_id` devuelto por una búsqueda por texto es la entidad más cercana, no la nombrada.**

### Lo que esto invalida, y hay que decirlo entero

**Los 71 resultados de la ronda 8 no tienen referente conocido**, porque la máscara no traía `displayName`. Eso incluye **el único `CLOSED_PERMANENTLY`**, el de Plaza Bar, que yo reporté como el acierto de la herramienta. **No sabemos de qué establecimiento hablaba.**

Y cae una frase mía que ahora no tiene sostén: escribí que *«Places distinguió un acto jurídico de un hecho operativo mejor que siete medios y mejor que yo»*. **No lo sabemos.** Puede haber contestado sobre otro local de la cuadra.

**Lo que no cae es la corrección de The New Brighton**, porque no se apoyaba en Places: se apoya en una reseña de mayo de 2026 posterior a la quiebra y en la ficha sin marca de cierre. Eso sigue en pie, y FD-20 también — con un segundo caso, el Palacio de la Papa Frita.

### Y dos defectos nuevos que son de primer orden

**Contradicción entre campos de la misma respuesta.** El Castelar volvió como **«EX Hotel Castelar.»** con estado `OPERATIONAL`. El campo de nombre trae el cierre que el campo de estado niega.

> **Regla: cuando dos campos de la misma respuesta se contradicen, no hay dato. Se resuelve la contradicción o se descarta la respuesta entera.** Quedarse con el campo que uno fue a buscar es elegir el resultado.

**No determinismo.** La misma consulta, dos minutos después, devolvió otro lugar, porque con `maxResultCount: 1` se toma el primero de una lista rankeada que no es estable.

> **Una fuente que contesta distinto a la misma pregunta no puede fundar ningún veredicto sin una restricción de identidad.** No es ruido: es que la unidad de análisis no está definida.

**Mi diseño de cuatro celdas sobrevive como diseño y cambia de objeto.** Ya no prueba qué significa el estado: **prueba si la respuesta es sobre quien preguntamos.** Cada celda necesita `displayName`, y una compuerta de identidad que rechace la respuesta si el nombre y la dirección no coinciden — como la que ya escribiste para el control de identidad, que dejó una sola falla real de once.

---

## R20: mi número estaba mal y yo lo amplifiqué

**41 % de superficie y 53 % de locales** era falso. Verificado: **47 % y 30 % — 31 locales, no 54.**

Y el mecanismo es el que más veces nos mordió: **el callejero guarda el mismo corredor bajo dos nombres.** `GARCIA DEL RIO AV.` cruza Cabildo, `GARCIA DEL RIO` cruza Balbín; se buscó el segundo, se pidió el cruce con Cabildo —que está en la otra mitad— y `tramo_entre` ancló 761 metros fuera del eje **sin avisar**.

**Es la tercera aparición de la misma familia**, después de `esq` matcheando adentro de «Esquiú» y de «INDEPENDENCIA AV.» contada como calle distinta de «Avenida Independencia». Las tres fallan en silencio y las tres son variantes de nombre de calle. **Ya no es un bug: es una propiedad del callejero que el proyecto tiene que tratar como tal**, con canonicalización y test de regresión con casos negativos.

Mi parte: tomé un número que no produje, lo puse en la errata con el rótulo **«CAMBIA UNA CONCLUSIÓN»** y reescribí mi propio documento con él. **La dirección era correcta —no es un residuo— y la magnitud estaba mal**, y el error que más me importa es que amplifiqué un dato ajeno sin poder verificarlo y sin decir que no podía.

### Y adentro de eso hay el peor número del día

> **El 46,6 % de la base no tiene `direccion_norm`.**

Casi la mitad de los locales no se pueden ubicar por dirección, y por eso el reparto de la cola de R20 se hizo **por eje más cercano**. Eso no es un detalle de esta corrida: **afecta a toda asignación de locales a zonas que no sea puramente geométrica**, y no está declarado en ninguna parte.

**Va a la Parte X de la edición técnica, entre los límites, con esas palabras.** Es más importante que la mitad de lo que escribí esta semana.

---

## Colegiales: propuse un perímetro entre dos avenidas que se encuentran

**Av. Álvarez Thomas y Av. Forest se tocan. Distancia 0 metros.** No encierran una banda, y yo propuse «la franja entre Álvarez Thomas y Forest» como si fueran paralelas.

De las cuatro calles que la fuente nombra, sólo **Zabala (254 m)** y **Virrey Avilés (344 m)** cruzan con tramo verificable. **Tres cuadras, no diez.** Delgado queda a 55 metros de Álvarez Thomas y Conde a 178: no cruzan nada, tocan la punta de la cuña.

**Es el error de Flores otra vez** —Boyacá y Carabobo son la misma avenida renombrada— y es la segunda vez. Yo escribí **R12: toda delimitación se verifica midiéndola**, y no la apliqué a mi propia propuesta, en el mismo documento donde citaba a Flores como el caso que la origina.

**La regla no falla en la lectura. Falla cuando el que propone es uno.**

Y aparece el dato que pedí verificar y complica los dos nudos a la vez: **Concepción Arenal entre Zapiola y Conesa mide 143 metros, cae 100 % en Colegiales por la capa de barrios, y el 47 % de su área está dentro de R01.** O sea que el Polo Concepción **está parcialmente adentro de Palermo**. No es una tercera cosa: es una pieza de la frontera Palermo–Colegiales, y hay que resolverla con Palermo y no aparte.

---

## Monserrat: dos en la capa contra nueve en el catálogo

Fui a mi propio archivo antes de opinar. **El 9 no es una inferencia mía**: sale del campo `barrio_catalogo`, que es el barrio que asigna el anexo de la Resolución 1225/26. Los nueve son El Colonial, Bar Iberia, Bar Seddon, el Cabildo, Café Tortoni, El Querandí, La Puerto Rico, London City y Los 36 Billares.

Así que la discrepancia es **entre el catálogo (9) y la capa cargada (2)**, y la explicación más probable es que la capa —225 hitos de todo tipo— no tiene los 90 del catálogo cargados. **No lo afirmo: es lo que hay que verificar.**

**Qué está en riesgo y qué no, que es lo que importa para la presentación:**

**La lámina 6 aguanta.** El 44 % de la Comuna 1 son 40 de 90, y San Nicolás, Monserrat, San Telmo y Retiro son **todos Comuna 1**. Como se repartan esos 40 entre los cuatro barrios no cambia el 40 ni el 44 %.

**La lámina 7 no aguanta sola.** *«Monserrat concentra 9 de los 90»* depende del reparto, y si la capa dice 2, cualquier número del Atlas calculado sobre la capa va a contradecir a la lámina delante de quien la lea.

Y hay una verificación que decide, y no es mía: **si el límite norte de Monserrat es Av. Rivadavia, los cuatro de Av. de Mayo —Iberia 1196, Tortoni 825, London City 599, Los 36 Billares 1265— son Monserrat y el catálogo acierta.** Si el límite fuera Av. de Mayo, la mitad se iría a San Nicolás. **Eso lo dice USIG, no yo.**

---

## Lo que hiciste bien y conviene que quede como método

**Agregar `displayName` y correr de nuevo cuando mi predicción se cumplió.** Ése es el mejor movimiento del día y merece nombre propio, porque va contra el instinto: la predicción había salido bien.

> **R15 · Una predicción que se cumple se audita igual que una que falla.**
>
> El momento de mayor riesgo del método no es el resultado inesperado —ése se investiga solo— sino el esperado. Si `displayName` no se agregaba, hoy tendríamos una hipótesis confirmada construida sobre una respuesta mal atribuida, y nadie iba a volver a mirarla.

**No abrir la ronda de Las Cañitas con el instrumento recién cuestionado.** Correcto, y lo hubiera pedido igual. La ronda de Cañitas no depende de Places —es documental— pero abrir cualquier cosa el día que se cae la atribución es cargar sobre un piso que se está revisando.

**Y no cargar FD-21 y FD-22 de memoria.** Es la regla más chica de las tres y la que más lejos llega.

---

## El balance, sin maquillar

De lo que produje en las dos últimas rondas:

**Se cayó** — la hipótesis de la resta de Palermo, por mi propio criterio de refutación · el perímetro de la franja de Colegiales, por imposible · las cifras 41 %/53 % de R20 · la frase de que Places había acertado mejor que la prensa · y el marco de dos ramas para Places, que preguntaba un piso más arriba de donde estaba el problema.

**Quedó en pie** — la corrección de The New Brighton, que nunca se apoyó en Places · **FD-20**, con dos casos · la mudanza del Palacio de la Papa Frita y lo que le hace a la lámina 11 · La Boca, que se movió y corrige mi capa de memoria · el censo de Las Cañitas · **el IDECBA**, que es lo más valioso de la semana y no dependía de nada mío · y la pregunta cero, que hoy sumó tres instancias más — dos de ellas mías y una en el texto donde la propuse.

Es aproximadamente la mitad. **Y la mitad que se cayó la tiró la geometría o una máscara de campos, no una discusión** — que es exactamente para lo que sirve tener el trabajo repartido en dos lados que no comparten los errores.
