# Cómo se lee el borrador de poligonización

**Escrito el 6 de agosto de 2026, ANTES de que el mapa exista.**

Ese orden no es una formalidad. Un borrador con N clusters no se interpreta solo: hay que
decidir qué es un polo, qué es ruido y qué es un polo partido en dos. Si el criterio se escribe
después de ver el mapa, se ajusta a la imagen que nos gustó. Es el mismo motivo por el que las
bandas de las pruebas de Places se escribieron antes de correrlas.

---

## 1 · Qué es un polo, dicho explícito

El Atlas nunca lo definió por escrito; lo aplicó. Puesto en palabras, un polo es **una
concentración de oferta gastronómica, reconocible en el territorio, con continuidad espacial y
tamaño suficiente para nombrarse.**

De ahí salen las cuatro pruebas que un cluster tiene que pasar. Ninguna sola alcanza.

| prueba | qué descarta |
|---|---|
| **Tamaño** | agrupaciones demasiado chicas para nombrarse |
| **Densidad** | manchas extensas y ralas que no son concentración |
| **Continuidad** | conjuntos de puntos lejanos entre sí que el algoritmo une |
| **No ser artefacto** | clusters que existen por cómo consultamos, no por lo que hay |

---

## 2 · Los umbrales se anclan en lo ya publicado, no se inventan

Regla: **el umbral se fija una vez, para toda la Ciudad, antes de mirar qué zonas sobreviven.**

Y se ancla en las zonas que la Dirección ya reconoce, que es el único punto de referencia
legítimo que tenemos:

- **Tamaño mínimo.** Las dos zonas publicadas más chicas con cifra son García del Río (≥40) y
  Boulevard Caseros (66). Un umbral por encima de eso excluiría zonas que la Dirección ya
  adoptó, así que el mínimo tiene que quedar **en el orden de 40, o por debajo**. Si el
  clustering necesita 100 para producir un mapa limpio, el problema es del mapa, no del umbral.
- **Densidad mínima.** Hay un antecedente medido: R07 Costanera Norte da 0,03 parcelas por
  hectárea contra 15,6 de la Ciudad, y **entre esos dos valores no hay ninguna zona**. Ese hueco
  natural en la distribución es el mejor lugar para cortar. Buscá el hueco antes de elegir un
  número redondo.
- **Continuidad.** Distancia máxima entre puntos vecinos dentro de un mismo cluster, declarada
  en metros. Las zonas multiparte existen —Palermo, Costanera Norte— pero en el Atlas se
  muestran **como partes separadas de una zona**, no como una mancha continua. Si el clustering
  une dos focos que el Atlas muestra separados, es el clustering el que está mal.

Si al aplicar el umbral una zona publicada desaparece, **no se baja el umbral para rescatarla.**
Se anota como divergencia y se explica. Bajar el umbral por zona es exactamente cómo se fabrica
un mapa que confirma lo que ya creíamos.

---

## 3 · Las tres pruebas de artefacto

Son nuevas y salen de todo lo que aprendimos esta semana. Un cluster que falla cualquiera de
las tres **no es un polo hasta que se demuestre lo contrario.**

### 3.1 · Artefacto de fuente

Si más del 70 % de los puntos de un cluster vienen de **una sola fuente**, el cluster puede ser
un artefacto de esa fuente. Se marca y se revisa.

Especialmente si esa fuente es Places, que ya sabemos que sirve una lista rankeada a
profundidad variable: un cluster de puros puntos de Places puede ser el resultado de haber
consultado ahí con más finura.

### 3.2 · Artefacto de grilla

Si los bordes de un cluster **coinciden con los bordes de las celdas de consulta**, el cluster
tiene la forma de nuestra grilla y no la de la oferta. Es medible: cruzar los contornos contra
la grilla usada y reportar coincidencia.

Es la versión espacial del defecto que ya tuvo el Atlas —ocho referencias cuyas envolventes
salieron de la geometría de consulta y no de la oferta—.

### 3.3 · Artefacto de cobertura

Un cluster en un barrio donde la base es notoriamente floja vale menos que el mismo cluster
donde la base es densa. Los dos indicadores de parejidad —gastronómicos sobre parcelas
comerciales, y locales cada mil habitantes— dan el contexto. **Todo polo candidato se reporta
junto con la parejidad de cobertura de su barrio.**

Y al revés, que es lo que más importa: **la ausencia de polo en un barrio con cobertura floja no
prueba que no haya polo.** No se puede escribir «no se identificaron polos en el sur» si el sur
tiene la mitad de cobertura relativa. Se escribe «con la cobertura disponible, no se
identificaron».

---

## 4 · El cotejo contra las 22 zonas: cuatro resultados, y el cuarto es el difícil

| resultado | qué significa | qué se hace |
|---|---|---|
| **Coincide** | el clustering encuentra la zona con forma parecida | confirma el Atlas. Es el caso bueno |
| **Difiere en extensión** | mismo lugar, otro tamaño | se reporta la diferencia y se explica por qué. No se ajusta ninguno de los dos todavía |
| **Polo nuevo** | el clustering encuentra concentración donde el Atlas no tiene zona | **candidato**, no polo. Pasa por las cuatro pruebas y por criterio de la Dirección |
| **Zona no encontrada** | el Atlas tiene zona, el clustering no ve nada | el caso incómodo. Ver abajo |

### Sobre el cuarto

Es el que hay que tratar con más cuidado, porque toca cifras publicadas y en revisión.

Tres explicaciones posibles, en este orden de probabilidad:

1. **La zona no era una concentración**, sino una lectura territorial de la Dirección. El Atlas
   lo admite para varias: «referencia dispersa» es literalmente eso. Una referencia dispersa
   **no tiene por qué producir un cluster**, y que no lo produzca la confirma, no la refuta.
2. **La cobertura de la base ahí es floja.** Se chequea con los indicadores de parejidad antes
   de concluir nada.
3. **La zona no se sostiene.** Es la última hipótesis, no la primera, y no se declara desde un
   borrador.

**Ninguna zona publicada se pone en duda a partir de este ejercicio.** El borrador no tiene
autoridad para eso: es un cálculo automático contra una lista que definió la Dirección a partir
del territorio que venía siguiendo. Lo que el borrador produce son **preguntas**, y se anotan
como tales.

---

## 5 · Lo que el algoritmo no decide

Conviene dejarlo escrito para que nadie lo suponga:

- **Qué polos entran al Atlas.** Es decisión de la Dirección.
- **Cómo se llaman.** Los nombres son de uso corriente y territorial, no salen de un cluster.
- **La familia territorial.** Las cinco familias describen forma de estar en el territorio; el
  algoritmo puede *sugerir* —un cluster alargado sobre una avenida sugiere eje o corredor, dos
  focos separados sugieren polo con partes— pero la asignación se revisa a ojo.
- **Los límites finos.** Una envolvente es una lectura de trabajo. Sigue sin ser un límite
  oficial, y el vocabulario del Atlas sobre eso no cambia.

---

## 6 · Qué reportar cuando el borrador esté

En este orden, y con esto alcanza para decidir el paso siguiente:

1. **Los umbrales elegidos, con su justificación**, y la evidencia del hueco de densidad.
2. **Cuántos clusters pasan las cuatro pruebas** y cuántos caen en cada una.
3. **La tabla de cotejo** contra las 22, con los cuatro resultados.
4. **Los candidatos nuevos**, ordenados por tamaño, con su barrio, la parejidad de cobertura de
   ese barrio, y de qué fuentes vienen sus puntos.
5. **Las zonas no encontradas**, con cuál de las tres explicaciones parece aplicar y por qué.
6. **Los clusters marcados como posible artefacto**, con cuál prueba fallaron.

Y un mapa que se pueda mirar. Un PNG de toda la Ciudad con los clusters y, encima, las 22
envolventes publicadas en otro color, alcanza para que la conversación siguiente sea concreta.

---

## 7 · Un recordatorio, para cuando el mapa esté lindo

El riesgo de este paso no es técnico. Es que un mapa completo de la Ciudad **parece más
verdadero de lo que es**: dibuja con la misma nitidez un polo apoyado en cinco fuentes que uno
apoyado en una, y con la misma nitidez un barrio bien cubierto que uno flojo.

Por eso la parejidad de cobertura va **al lado de cada polo**, no en una nota al pie. Y por eso
el borrador no se muestra fuera del equipo hasta que esa columna esté.
