# Aviso sobre `grilla_places_48_barrios.csv`

**Fecha:** 5 de agosto de 2026
**Estado del archivo:** intacto. **No se recalculó ninguna celda.**

El CSV sigue siendo el que se calculó el 5/8 a la mañana: 1.190 celdas de 500 m para los 204 km²
de la Ciudad, 2.100 requests estimados con paginación. Este aviso existe para que nadie lo use sin
saber que **el criterio con el que se dimensionó ya no es el que corresponde**, y para dejar
escrito por qué todavía no se rehizo.

## Con qué criterio se armó

Una celda cada 0,25 km² y una celda cada 40 locales esperados, tomando el mayor de los dos. El
universo esperado por barrio salía de dividir las direcciones núcleo por el factor de captura
documental (18,2 %). Es una grilla **dimensionada para contar**: la densidad está puesta para que
ninguna celda se sature y así no se pierdan locales en silencio.

## Por qué ese criterio ya no aplica

Places no cuenta. Recupera del orden del 12 % de una cifra contada a pie y ese 12 % es techo
estructural de la fuente —dos corridas de la misma consulta comparten el 81,6 % de sus resultados
y la segunda agregó un solo local—. Dimensionar una grilla para que no se sature es resolver un
problema que la fuente no tiene: lo que la limita no es el tope de 60 resultados por consulta, es
el corte del ranking, que aparece mucho antes.

## Con qué criterio hay que rehacerla

Lo que Places sí hace es **descubrir**: en 11 de las 14 zonas con muestra suficiente, la mayor
parte de lo que devuelve son direcciones que el padrón no tiene. Para descubrimiento el criterio
de diseño es otro y va en dirección contraria a lo que se suponía cuando se congeló esto:

- **la densidad no se puede bajar «porque alcanza con muestrear»**. Refinar la celda es lo único
  que baja el corte del ranking, así que menos densidad es menos descubrimiento, no el mismo
  resultado más barato;
- **la familia C (heladería) se descarta**: aportó cero locales nuevos sobre Villa Crespo. La B
  (parrilla, pizzería, comida al paso) aportó 18 sobre 63 y paga lo que cuesta. Con dos familias
  en vez de tres se ahorra un tercio del costo por celda;
- **el orden de los barrios ya no es por universo esperado**, que era una cuenta de conteo. Si el
  objetivo es descubrir, conviene empezar donde el padrón está más desactualizado, y eso ahora se
  puede medir: la proporción de lo que Places trae que el padrón ya tiene va del 7,1 % al 81,8 %
  según la zona.

## Por qué no se rehizo todavía

Porque rehacerla es una decisión sobre el gasto —cuántos requests se autorizan y para qué—, y ésa
es de Diego. El criterio está escrito acá para que la decisión se tome sobre algo, no para
adelantarla. **Mientras tanto el CSV no se toca**, por la misma razón por la que no se tocó la
spec cuando estaba congelada: reescribirlo dos veces pierde la trazabilidad de por qué cambió.
