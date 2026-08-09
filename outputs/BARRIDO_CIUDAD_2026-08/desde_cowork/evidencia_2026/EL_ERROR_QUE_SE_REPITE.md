# El error que se repite

*8 de agosto de 2026 · a propósito del bug del denominador*

---

## El hallazgo del repositorio vale más que el conteo que fue a buscar

Pedí reconciliar una suma que no cerraba: 27 + 23 = 50 sobre 51 filas. La respuesta no fue «falta la fila tal». Fue **un bug con nombre y mecanismo**, y de la familia que ya teníamos catalogada: falla sin excepción, y el resultado se explica bien con la hipótesis equivocada.

```python
soporte.area / zonas[candidatas[0]]["geom_zona"].area > 0.5
```

La prueba descartaba las filas que abarcan el barrio entero dividiendo por el área de la zona candidata. **Funcionaba mientras todas las zonas se medían sobre el barrio.** Dejó de funcionar en la misma ronda, unas líneas más arriba, cuando Z24 y Z39b pasaron a medirse sobre su perímetro delimitado —39,5 y 34,9 hectáreas contra las 859 del barrio— porque tres zonas comparten Flores.

Con ese denominador, la pregunta dejó de ser *«¿esto abarca el barrio?»* y pasó a ser *«¿esto es más grande que media Z24?»*. Y `PGR_P014 · Flores`, que es el **5,3 %** del barrio, daba **116 %**.

**El nombre de la variable no cambió. Lo que denotaba, sí.**

Es un mecanismo nuevo y merece quedar escrito: **un proxy que deja de ser proxy.** El código decía «el área de la zona» y significaba «el área del barrio», y eso era cierto sólo porque en los datos viejos las dos cosas coincidían. La corrección que hizo bien el proyecto —medir las zonas sobre su perímetro y no sobre el barrio— fue la que rompió el supuesto, y lo rompió **en la misma corrida**.

---

## Pero lo que importa es lo otro, y es más grande

El bug produjo **una tercera clase**: «la fila no tiene zona resuelta». Y esa clase se reportó como si fuera una categoría del territorio.

Parecía legítima. Se parece a `requiere_cruce`, que sí es una categoría real. **La salida del bug era indistinguible de un estado verdadero de la ontología** — y por eso yo la incorporé a la edición técnica sin sospechar, y sólo la marqué como pendiente porque la suma no cerraba. Si 27 + 23 hubiera dado 51, la tercera clase seguiría publicada como un hecho sobre Flores.

**La aritmética fue lo único que lo delató.** Vale registrarlo así, porque no siempre va a haber una suma que no cierre.

---

## Y ahora la parte que hay que decir en voz alta

Este error ya nos pasó cinco veces. **Son cinco instancias del mismo error, no cinco errores distintos.**

| # | lo que dijimos | lo que era en realidad |
|---|---|---|
| 1 | «No se identificaron zonas en el extremo sur de la Ciudad» | una afirmación sobre **dónde miramos** |
| 2 | «La vía B abre en 7 filas de 94» | una afirmación sobre **el tamaño de los polígonos** |
| 3 | «Hay una tercera clase de filas sin zona resuelta» | una afirmación sobre **un denominador roto** |
| 4 | «El catálogo falla con los establecimientos alojados dentro de otro inmueble» | una afirmación sobre **dos casos que compartían algo irrelevante** |
| 5 | «Setenta establecimientos operativos» | una afirmación sobre **la ausencia de señal de una API** |

En los cinco casos, el enunciado era gramaticalmente una afirmación sobre el territorio y materialmente una afirmación sobre el instrumento. En los cinco, la versión instrumental es la verdadera. Y en los cinco, **el enunciado falso era el más interesante de los dos** — por eso se publicó.

Ése es el patrón: **la lectura territorial siempre es la más noticiosa.** «El sur no tiene gastronomía» es una noticia; «no miramos el sur» es un trámite. «Los bares notables están cerrados» es una noticia; «los polígonos son chicos» es un detalle técnico. El sesgo no es de descuido: es de atractivo.

R7 —*«no encontramos» no es «no existe»*— es un caso particular de esto, el de las ausencias. Pero el error también viene con signo positivo: los setenta `OPERATIONAL` no son una ausencia, son una presencia falsa. **R7 cubre la mitad del problema.**

---

## La pregunta cero

Por eso propongo que esto no sea la regla catorce sino que vaya **antes** de las nueve preguntas de control, como pregunta cero, con esa palabra:

> **¿Esto que estoy por afirmar es una propiedad del territorio, o una propiedad de mi instrumento?**
>
> Si es del instrumento, se escribe como propiedad del instrumento. Aunque sea menos interesante. **Sobre todo si es menos interesante.**

Y una regla operativa que sale de la tercera clase, ésa sí numerada:

> **R14 · Una clase que aparece en un resultado y no estaba en el diseño se trata como sospecha de instrumento hasta que se la pueda producir a propósito.**
>
> Si no se puede escribir el caso que la genera y reproducirlo, no es una categoría del territorio: es una salida que todavía no se entiende.

Es exactamente lo que faltó con la tercera clase, y lo que sí se hizo —tarde pero se hizo— con la hipótesis del contenedor: doce verificaciones para matarla.

---

## La familia de las reglas, que el repositorio nombró bien

El repositorio observó, al cargar R9 a R13, que las cinco nuevas tienen aire de familia. Es cierto y conviene fijarlo como estructura del método:

| bloque | de qué salieron | qué preguntan |
|---|---|---|
| **R1–R8** | la fase de medición | **¿el número es correcto?** — controles, umbrales, curvas, presupuesto, campos vacíos |
| **R9–R13** | la fase documental | **¿a qué objeto pertenece este dato?** — a qué capa, a qué fila, a qué fecha, a qué geometría, a qué entidad |
| **R14 + pregunta cero** | esta reconciliación | **¿de qué estoy hablando: del territorio o del instrumento?** |

Los tres bloques fallan distinto. R1–R8 fallan produciendo un número equivocado. R9–R13 fallan produciendo un número correcto atribuido al objeto equivocado — que es peor, porque el número resiste cualquier verificación aritmética. Y R14 falla produciendo **un objeto que no existe**, que es lo peor de los tres, porque no hay contra qué verificarlo.

---

## Dos correcciones mías, chicas, del mismo día

**Dije que las seis preguntas pasaban a nueve, y eran siete.** R8 había agregado una séptima —*«¿algún campo pedido llegó vacío en el 100 % de las filas?»*— que yo no tenía. Las mías entraron como 8, 9 y 10, sin pisar nada, porque el repositorio miró el archivo antes de escribir.

**Es la tercera vez que afirmo el contenido de un archivo que no puedo leer.** Las anteriores fueron los cinco hitos de Monserrat y los dos de Barracas. Ya no es un descuido repetido: es una consecuencia estructural de que produzco afirmaciones sobre un repositorio al que no tengo acceso de lectura. **La regla R9 existe y yo no la puedo ejecutar** — la ejecuta el repositorio, después, encontrando lo que yo mandé de más. Por eso el pedido del volcado de la capa es el cambio de proceso que más rinde de todos los pendientes: convierte R9 de una regla que alguien aplica a mi trabajo en una regla que yo puedo aplicar antes de entregarlo.

**Y la tabla de correspondencia tenía tres filas que no eran archivos.** Escribí `vigencia_verificada_ronda_1.csv, _ronda_2.csv` usando la abreviatura tipográfica de la fila anterior, en una tabla que después se leyó como lista de rutas. El repositorio no la transcribió: **la verificó contra disco**, encontró 39 de 42, y marcó las tres con `existe = no` en vez de borrarlas — con el argumento correcto, que es que una tabla de trazabilidad que nombra archivos ausentes promete algo que no tiene, y esconderlos es peor que listarlos.

De ahí sale un corolario de **R6**, y lo dejo como corolario y no como regla nueva a propósito, porque una lista de reglas que crece sin parar deja de leerse:

> **En una tabla de trazabilidad no se abrevia: cada fila lleva el nombre completo. Y se verifica contra disco, no se transcribe.**

---

## Lo que esto le hace al documento

En la edición técnica, la pregunta cero va **antes** de la Parte IX, no adentro. Las nueve preguntas de control se aplican a un resultado; ésta se aplica a la frase con la que se lo va a escribir, que es un momento posterior y distinto.

Y hay una consecuencia de redacción que atraviesa el Atlas entero y conviene que quede como instrucción y no como aspiración: **cada afirmación de ausencia y cada afirmación de estado lleva su sujeto real.** No «el sur no tiene concentraciones» sino «no las buscamos ahí». No «setenta establecimientos operativos» sino «setenta consultas sin señal de cierre». No «la zona no tiene trayectoria» sino «el fragmento no contiene hitos».

Es más largo de leer y es lo único que hace que el documento envejezca bien.
