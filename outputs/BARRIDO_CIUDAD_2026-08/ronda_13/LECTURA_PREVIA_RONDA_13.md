# Lectura previa · Ronda 13 · 2026-08-09

Escrita **antes** de correr nada, por R1. Google Places: **0 requests** en toda la ronda.

Lo que sigue son predicciones con número, para que la corrida pueda refutarlas. Si acierto,
no aprendí nada; si fallo, la ronda sirvió.

---

## Palermo · las tres subzonas que nadie midió (tarea 7, y con ella la 5)

`fichas_corpus_polos.csv` fila R01 nombra **seis** subzonas: P091 Soho, P078 Hollywood,
P065 Las Cañitas, **P073 Palermo Botánico, P087 Palermo Pacífico, P092 Villa Freud**. Las
rondas 9 y 10 midieron R01 contra las tres primeras nada más. El residuo que quedó son
**108,5 ha y 188 locales en 8 piezas**, la mayor de 40,17 ha y 134 locales.

La hipótesis a probar es la que abre la tarea: **si la pieza 1 corresponde a una de las tres
que faltan, Palermo se cierra entero.**

### Predicción 1 — y va en contra de la hipótesis

**Las tres intersecciones van a dar cero, o casi.**

No lo digo por intuición. `borrador_polos/POLOS_PARA_NOMBRAR.csv` ya trae calculada la columna
`zonas_publicadas_encima`, y para las tres dice literalmente **`ninguna`**:

| polo | nombre | locales | ha | zonas publicadas encima |
|---|---|---:|---:|---|
| P073 | Palermo Botánico | 207 | 39,19 | **ninguna** |
| P087 | Palermo Pacífico | 56 | 5,80 | **ninguna** |
| P092 | Villa Freud | 79 | 11,71 | **ninguna** |

Si esa columna es correcta, ninguna de las tres toca R01 y **la pieza 1 no puede ser ninguna
de ellas.** Palermo no se cierra: la pieza 1 sigue sin nombre y hay que ponérselo.

### Predicción 2 — el candidato que la ficha no nombra

Si la pieza 1 no es ninguna de las tres, ¿qué es? En el mismo archivo hay un polo que la ficha
de R01 **no** lista y que sí está adentro:

> **P090+P089 · «Palermo — eje Av. Santa Fe»** · 104 locales · 18,54 ha ·
> `zonas_publicadas_encima = R01 Palermo (68 % del polo, 5 % de la zona)`

Predigo que **la pieza 1 contiene a P090+P089 o se solapa fuerte con él**, y que el nombre de
la pieza 1 va a salir de ahí. Contra: la pieza 1 mide 40,17 ha y P090+P089 mide 18,54 — le
sobraría menos de la mitad. Así que si acierto, acierto a medias.

### Predicción 3 — la aritmética que tiene que cerrar

Si las tres dan cero, el residuo de 188 locales **no se mueve ni un local**. Ese es el control:
cualquier corrida que cambie el 188 mientras las tres intersecciones dan cero está mal.

### Qué me haría cambiar de opinión

Que `zonas_publicadas_encima` esté desactualizada. Se calculó sobre `borrador_polos_v3` contra
las 22 zonas, y desde entonces la geometría **se tocó** —la ronda 7 movió polígonos y abrió seis
solapes nuevos—. Por eso la corrida mide de nuevo y no lee la columna.

---

## La vía C de Almagro (tarea 4)

**Predigo que la vía C de Almagro NO abre, y no por lo que dice la pregunta.**

La pregunta plantea «¿mercado o feria itinerante?». Predigo que la respuesta es **ninguna de las
dos: no hay objeto**. Almagro nunca nombró el objeto que le abre la vía C. Toda otra zona que la
abre nombra el suyo —Bonpland, Belgrano, del Progreso, Patio Costanera Norte—; Almagro dice
«abre» y nada más, y lo único que el corpus llega a nombrar cerca es la feria itinerante de
Plaza Almagro, mencionada como **puerta cerrada** (los permisos son internos).

Si es así, no hace falta la decisión 23: **la decisión 1 ya resolvió esta clase el 07/08** —«la
vía C exige mercado, patio o galería en actividad; la FIAB no abre»— y mandó revisar Z47
Monserrat por exactamente el mismo motivo.

Control que lo probaría: **ningún hito de tipo `Mercado/patio` de la capa cae en Almagro.**

---

## Lo que no voy a hacer en esta ronda

- No toco el pipeline público, ni las láminas, ni las secciones del documento.
- No renombro nada del catálogo de hitos ni de la matriz vigente.
- No ejecuto una sola consulta paga.
