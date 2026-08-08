# El reparto de las 51 sin_hitos cierra en 28 + 23, y la fila que faltaba es PGR_P014

*8 de agosto de 2026 · responde el pendiente declarado en la sección 31 de
`EDICION_TECNICA_FASE_DOCUMENTAL.md`*

---

## La pregunta

El reparto de las filas cuya vía B no encuentra hitos **dentro de su propio polígono** se venía
reportando como **27 + 23 = 50**, y las filas a repartir eran **51**. Faltaba una.

## La respuesta corta

**El 51 es el número correcto.** La fila que faltaba es **`PGR_P014 · Flores`** (45,63 ha, 61
locales), y cae en **«la zona SÍ tiene hitos, el fragmento no»**, que pasa de 27 a **28**.

El reparto queda:

| | filas |
|---|---|
| la zona SÍ tiene hitos, el fragmento no | **28** |
| la zona tampoco tiene hitos | 23 |
| **total** | **51** |

**Dos clases, no tres.**

## Por qué faltaba, que es lo que importa

No era un error de suma ni un pendiente de asignación: era **un bug en el clasificador de la
ronda 7**, y de la familia que este proyecto ya tiene catalogada — falla sin tirar ninguna
excepción y produce un resultado que se explica bien con una hipótesis equivocada.

La tarea 4 de la ronda 7 resolvía las filas trabadas por cruce espacial, y antes de cruzar
descartaba las que **abarcan el barrio entero** en vez de pertenecer a una de sus zonas —el caso
de `PGF2_FLORES`, cuyo soporte es el barrio de Flores completo—. La prueba era:

```python
abarca_el_barrio = (soporte.area / zonas[candidatas[0]]["geom_zona"].area) > 0.5
```

El denominador es **el área de la primera zona candidata**, y eso funcionaba mientras todas las
zonas se medían sobre el polígono del barrio. Dejó de funcionar en la misma ronda, unas líneas más
arriba: Z24 y Z39b pasaron a medirse sobre **su perímetro delimitado** —39,5 y 34,9 ha, contra las
859 ha del barrio de Flores— porque tres zonas comparten ese barrio y el barrio contaba los mismos
hitos tres veces.

Con ese cambio, la prueba dejó de preguntar «¿este fragmento es más grande que medio barrio?» y
pasó a preguntar **«¿es más grande que media Z24?»**. `PGR_P014` mide 45,63 ha —el **5,3 %** de
Flores— y contra las 39,5 ha del corredor de Z24 daba 116 %: quedaba marcado como «abarca el
barrio entero» y salía sin zona asignada. Sin zona, no hay vía B de zona contra la cual comparar,
así que caía en una tercera clase residual que no debería existir.

**La corrección** es usar el barrio como denominador, que es lo que la prueba siempre quiso decir:

```python
area_barrio = marco_de(capa_barrios, [barrio_fila]).area
if soporte.area / area_barrio > 0.5:
```

Con eso `PGR_P014` vuelve al camino normal: no toca ninguna zona delimitada de Flores —está a
225 m de Z39b y a 1.747 m de Z24— y se asigna **por residuo a Z23**, igual que los otros cinco
fragmentos de Flores. Z23 tiene un hito de vía B (La Farmacia, verificado abierto), así que la
fila cae en «la zona sí tiene, el fragmento no».

## Lo que cambia y lo que no

- **Las filas resueltas de la tarea 4 pasan de 8 a 9 de 10.** La única que queda sin resolver es
  `PGF2_FLORES`, y queda bien: su soporte **sí** es el barrio entero (859,4 ha), que es el caso
  para el que la prueba existe.
- **`via_B_modo` en `requiere_cruce` baja de 5 a 4.**
- **Ningún otro número se mueve.** La vía B por zona sigue en 39 de 94 con la capa r8, y el total
  de filas sin hitos en su fragmento sigue siendo 51.

## De qué regla es este caso

De **R12** —toda delimitación se verifica midiéndola— y de **R8**, por la familia: un cambio
correcto en un lugar rompió una prueba en otro, sin error y sin ruido, y el resultado se leía como
un pendiente de asignación en vez de como un bug. La tercera clase «la fila no tiene zona
resuelta» era el síntoma, y se estaba reportando como si fuera una categoría del territorio.
