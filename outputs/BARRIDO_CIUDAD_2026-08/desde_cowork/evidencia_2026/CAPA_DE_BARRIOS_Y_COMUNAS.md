# La capa de barrios y comunas, incorporada y controlada

**10 de agosto de 2026** · archivos en `insumos/caba_barrios.geojson` y `insumos/caba_comunas.geojson`

---

## Qué se incorporó, y de dónde sale

| | |
|---|---|
| **origen inmediato** | repositorio público `OpenDataCordoba/barrios` en GitHub, commit `cfb3f50`, obtenido por clon público el 10/08/2026 |
| **fuente original, declarada por el propio repositorio** | los **dos recursos oficiales de Buenos Aires Data** — el de barrios y el de comunas |
| **barrios** | 48 polígonos · 663.361 bytes · `sha256 56bf0f53fcb425eb290335c193c02088…` |
| **comunas** | 15 polígonos · 1.141.556 bytes · `sha256 065200a847b1e022e060263a2a2cc448…` |
| **proyección** | EPSG:4326 · las dos capas |
| **validez geométrica** | 48 de 48 y 15 de 15 |

> **Lo importante de la primera fila es la segunda.** No es una capa de un tercero que se parece a la
> oficial: **es la capa oficial del Gobierno de la Ciudad, espejada en GitHub.** El repositorio cita
> textualmente los dos recursos de Buenos Aires Data —los mismos que devolvían error 503 al
> intentar bajarlos—. Se adopta el espejo **declarando que es un espejo**, con su hash, para que
> cualquiera pueda cotejarlo cuando el servidor oficial vuelva.

**Cuarenta y ocho barrios y quince comunas es exactamente lo que la Ciudad tiene.** No es un control
menor: descarta de entrada un recorte parcial o una versión con divisiones distintas.

---

## El control, que era obligatorio antes de usarla

El atlas ya venía usando **27 polígonos de barrio** como provisorios de zonas sin perímetro. Si la
capa nueva no coincidiera con ésos, cambiarían las cifras que ya se publicaron.

Se midió con la regla de siempre —**superficie perdida, no `covers()`**— y el resultado es:

**Veinticuatro de veintisiete coinciden dentro del 0,09 %.** El residuo son unos 1.500 m² sobre
cientos de hectáreas: ruido de proyección, no diferencia de territorio.

**Y los bordes exteriores de las dos capas coinciden a cuatro decimales** —de −58,5315 a −58,3352 en
longitud y de −34,7053 a −34,5265 en latitud—. Son el mismo objeto.

### Tres no coinciden — y el diagnóstico correcto es el opuesto del que escribí

**Mi primera lectura fue que tres polígonos del atlas eran más grandes que su barrio.** Medido
contra las dos capas a la vez, resulta falso en dos de los tres casos:

| zona | contra la capa que el atlas venía usando | contra la capa oficial |
|---|---:|---:|
| **Z41 Núñez** | **0 m²** | 74.837 m² |
| **Z45 Belgrano** | **0 m²** | 65.152 m² |
| **Z46 Retiro** | 149.485 m² | 156.196 m² |

**Núñez y Belgrano son exactamente el polígono administrativo** —diferencia simétrica cero contra la
capa vieja— y sus campos son exactos. **Toda la diferencia está entre las dos capas de barrios, no
entre el atlas y el barrio.**

**Sólo Retiro sumó algo**, y su propio campo ya lo declara: 149.485 m² y 117 locales de la subzona
del clúster coreano, **el 100 % en San Nicolás.**

> **Lo que yo tomé por un defecto del atlas era una diferencia entre dos versiones de la misma capa
> oficial.** Medido sobre los 48 barrios, **los cuatro que difieren más del 0,5 % son Recoleta,
> Palermo, Núñez y Belgrano: los cuatro del frente costero.** Es la línea de ribera, que se
> redibuja entre versiones — **y no lleva locales**: cero en Núñez, uno en Belgrano.

### La decisión que sí queda abierta, y es de una línea

**Adoptar la capa oficial para todo el proyecto, o seguir con la que veníamos usando.** No es un
parche por zona: la función que sirve los barrios alimenta varias rondas, y cambiarla **movería el
conteo de doce barrios**, con un neto de **+1 local**.

**Conviene adoptar la oficial** —es la única con procedencia y hash— pero es una decisión de
conducción, porque toca números que ya circularon.

> **Y una trampa que conviene levantar antes de que muerda:** la capa vieja escribe **«La Boca»** y
> la oficial escribe **«Boca»**. Cualquier cruce por nombre pierde el barrio entero **en silencio**.

---

## Para qué se usa, y para qué no

**Se usa como base cartográfica.** Los quince mapas hoy se orientan con los 27 polígonos de barrio
que había en el repositorio. Con esta capa pasan a tener **los 48 barrios y las 15 comunas**, que es
lo que convierte un conjunto de manchas en un mapa que se lee solo.

**No se usa para delimitar polos.** Un polo no es un barrio — el atlas lo dice en su definición y lo
acaba de mostrar con números: **Almagro trazado son 25,79 hectáreas contra las 405,3 del barrio.**
La capa entra como referencia de lectura, y en ningún caso como perímetro.
