# Auditoría de duplicados · 29 riesgos, tres de ellos altos

*7 de agosto de 2026 · antes de poligonizar*

Datos en `auditoria_duplicados.csv`.

Se auditaron ocho familias de riesgo: geometría, nombres, homónimos, hitos en dos zonas, dobles registros, doble numeración, réplicas de prensa y enclaves. **Veintiséis riesgos están resueltos o son inofensivos. Tres son altos y hay que resolverlos antes de publicar cualquier agregado.**

---

## La buena noticia primero: los 124 polígonos no se pisan

Medido sobre `polos_publicables.geojson`:

| | |
|---|---|
| suma de las áreas individuales | **3.128,5 ha** |
| área de la **unión** | **3.128,5 ha** |
| solapamiento | **0,0 ha · 0,0 %** |

**Los 124 son disjuntos.** HDBSCAN produce clusters que no se superponen, y eso significa que **sobre ese conjunto los agregados se pueden sumar sin corrección**.

De ahí sale una cifra publicable y limpia: **12.688 locales en 3.128,5 hectáreas**. Sobre una base de 23.981 locales relevados, es el **53 % de la gastronomía relevada de la Ciudad concentrada en el 15 % de su superficie**.

Esa es la clase de número que sirve para la presentación, y ahora está calculado sobre la unión y no sobre una suma.

---

## Los tres riesgos altos

### G-01 · La matriz de 94 filas no es una partición de la Ciudad

Y no debería serlo: es un **instrumento de comparación**, que pone deliberadamente lado a lado objetos que se pisan —un barrio administrativo, sus fragmentos del clustering y la envolvente publicada de la misma área— para poder medirlos con la misma vara.

El problema aparece solo si alguien la suma. Y si se suma:

- **16.499 locales** sobre una base de 23.981. Sería decir que el **69 %** de la gastronomía de la Ciudad está dentro de polos.
- **7.731 hectáreas** sobre las ~20.300 de CABA. Sería decir que los polos cubren el **38 % del territorio**.

Las dos cifras están infladas por solapamiento. **La regla es simple: la matriz de 94 no se suma nunca.** Cualquier agregado se calcula sobre la unión de los polígonos publicables.

### G-02 · Flores está contado siete veces

`PGF2_FLORES` es el barrio entero: 773 locales, 859 hectáreas. Adentro hay **seis fragmentos del clustering** —P014, P036, P058, P059, P060 y P061— que suman 270 locales y 85,7 hectáreas.

Sumando las siete filas, Flores da **1.043 locales cuando el barrio tiene 773**. Doscientos setenta locales contados dos veces: **35 % de inflación en un solo barrio**.

Con la decisión 14 esto se resuelve solo: los seis fragmentos se asignan por cruce espacial a Z23, Z24 o Z39, y el barrio administrativo deja de ser una fila publicable.

### G-03 · Palermo es el caso raro, y no se resuelve solo

Soho (772 locales) + Hollywood (595) + Las Cañitas (361) suman **1.728 locales en 277 hectáreas**. La referencia publicada R01 Palermo mide **1.358 locales en 271,29 hectáreas**.

**Las subzonas tienen más locales que la referencia que supuestamente las contiene.** No están anidadas: son objetos distintos que se pisan parcialmente.

Y esto no lo arregla ninguna de las veinte decisiones. Hay que elegir: **o R01 se amplía para contener a las tres subzonas, o las subzonas son las fichas y R01 deja de ser una fila. Las dos cosas no pueden convivir en un agregado.**

Es la única decisión de delimitación nueva que aparece de esta auditoría.

---

## Cuatro solapamientos de hito que siguen abiertos

Son casos donde el mismo Bar Notable está reclamado por dos filas. Ninguno infla un conteo si se resuelve la atribución, pero hay que resolverla.

**El más importante: R12 Centro y Z47 Monserrat se pisan sobre el eje Av. de Mayo.** La Puerto Rico y El Querandí aparecen en las dos. **Cómo se reparten los nueve Notables de Monserrat entre las dos filas es la decisión de delimitación más grande que queda.**

Los otros tres: **La Giralda** en R02 y R12; **Bar Conde** en R19 y Z43 Colegiales, que la ampliación de R19 hacia Fraga y Dorrego puede agravar; y **El Símbolo y El Banderín** en R13 Abasto y Z37 Almagro, que ya estaba señalado para cuatro direcciones más.

---

## El error inverso, que es más peligroso

Contar de más se nota. **Fusionar dos locales distintos en uno no se nota nunca**, y encontramos cuatro casos donde estuvo a punto de pasar:

- **El Buzón** (Esquiú 1393, Nueva Pompeya, el de Homero Manzi) y **El Viejo Buzón**, que es otro local y es una de las diez sedes reales del Tango BA 2026. **Son dos hitos.**
- **La Perla de Caminito** y **La Perla del Once**, que cerró el 14 de enero de 2017 y en cuyo local funciona la pizzería La Americana. Una guía turística las listaba como dos locales distintos vivos, y eso fue lo que delató que su padrón era caduco.
- **El Fortín** (Álvarez Jonte 5299, Monte Castro) y **El Ferroviario** (Reservistas Argentinos 219, Liniers).
- **Café Roma** y **Roma del Abasto**, que el repositorio encontró fusionados en una sola fila, con una dirección inventada —"San Luis 3101"— y las coordenadas reasignadas. **Esa dirección falsa era mía.**

---

## Lo que ya está resuelto y no hay que volver a mirar

**Cinco locales con dos o tres nombres**, todos unificados: Bárbaro ("Bar Bar O" en el catálogo), La Perla de Caminito con tres grafías, Café Palacio que hoy es Museo Fotográfico Simik, Café Don Juan que la prensa llama Bar Don Juan, y la Salteñería El Conejo que veníamos escribiendo como Salchichería.

**Cuatro locales con dos registros oficiales**: Miramar es Bar Notable *y* Restaurante Icónico; El Fortín es Sitio de Interés Cultural *y* Pizzería Emblemática; El Tokio y Bar Oviedo tienen doble reconocimiento. **Son un hito con dos registros, no dos hitos.** Con la decisión 18 el campo `registro_oficial` admite varios valores: hay que usarlo como lista y no duplicar la fila.

**Ocho casos de doble numeración**, resueltos por la decisión 20 — con dos excepciones que hay que tratar aparte: **Marte** (Crisólogo Larralde 277 contra 2772) y **La Media Costilla** (Bahía Blanca 2300 contra Arregui 4000) no son doble numeración sino error o mudanza. No cargarlos sin verificar.

**Seis réplicas de prensa** ya descontadas de la vía E. Sin ese filtro, Colegiales y Retiro habrían contado el doble de grupos de los que tienen.

**Y tres enclaves coreanos que no son duplicados sino tres momentos de un mismo movimiento**: el núcleo del Bajo Flores, la extensión comercial de Ruperto Godoy y el desplazamiento a Retiro documentado en 2019 y ratificado en 2026. La ficha tiene que contar la secuencia, no repetir el enclave.

---

## Lo que hay que hacer, en orden

1. **Escribir la regla en la edición técnica:** la matriz de 94 no se suma. Los agregados van sobre la unión.
2. **Decidir Palermo** — es la única decisión nueva que aparece acá.
3. **Repartir los Notables de Av. de Mayo** entre R12 y Z47.
4. **Resolver las otras tres atribuciones** de hito compartido.
5. **Publicar el número limpio:** 12.688 locales en 3.128,5 hectáreas, el 53 % de la gastronomía relevada en el 15 % de la superficie.
