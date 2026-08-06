# Cuándo dos polos cercanos son uno

**Reconstruido de las decisiones ya tomadas en el proyecto · 6 de agosto de 2026**

La pregunta —por qué dos concentraciones cercanas no son una— ya se resolvió tres veces en este
proyecto, con criterios explícitos y números guardados. No hay que inventar una regla: hay que
leer la que se usó.

Está en `outputs/polos_gastro/corrida_territorial_v3/MATRIZ_DECISION_TERRITORIAL_V3.csv`, con
los archivos de sensibilidad al lado.

---

## 1 · Los tres precedentes

### Recoleta — nueve núcleos, una zona

| modelo | decisión | motivo textual |
|---|---|---|
| **REC-A** | **elegido** | «Los nueve núcleos forman una red continua; unidad general más parsimoniosa» |
| REC-B (dos subzonas) | respaldo | «Dos subzonas son posibles, pero agregan una división no imprescindible» |
| REC-C (multiparte) | descartado | «La multiparte no mejora la lectura porque la red analítica ya es continua» |

Y el dato que lo vuelve obvio: `RECOLETA_VACIOS_CONTINUIDAD_V3.csv` mide el vacío entre cada par
de núcleos. **Tres pares están a 0,0 metros** — se tocan. Otros tres están a 3, 6 y 10 metros.
La mediana de los catorce pares medidos ronda los 25 metros, y el máximo es 208.

No eran nueve polos separados por algo. Eran nueve pedazos de un tejido continuo que el
algoritmo había subdividido. La continuidad medida dio **1,0**.

### Belgrano — tres, y el motivo del rechazo es lo importante

`BELGRANO_SENSIBILIDAD_CONTINUIDAD_V3.csv` barre el umbral:

| umbral | componentes | tamaños |
|---:|---:|---|
| 80 m | 6 | 5; 5; 2; 2; 2; 1 |
| 120 m | 6 | 5; 5; 2; 2; 2; 1 |
| **160 m** | **3** | **8; 7; 2** |
| 200 m | 2 | 8; 9 |
| 250 m | 1 | 17 |

Se eligió 160 m y tres partes. El motivo del rechazo de la alternativa es la frase clave de todo
este asunto:

> «A 120 m aparecen seis fragmentos; **elegir cuatro sería arbitrario**.»

No se rechazó por distancia. Se rechazó porque **la cantidad de partes no era estable** y porque
los fragmentos de tamaño 2, 2, 2 y 1 son polvo, no centralidades. A 160 m emergen tres piezas de
8, 7 y 2 —Barrio Chino, Bajo Belgrano y Belgrano R— y la de 2 sobrevive **porque tiene respaldo
documental**, no por su tamaño.

### Costanera Norte — cuatro, y los vacíos se preservan a propósito

Separaciones entre componentes: 163, 462, 692, 1.418, 1.995 y 2.727 metros. Decisión anterior
(DEC-10) fija cuatro componentes **y la preservación de los vacíos**. Acá unir habría sido
inventar una línea que no existe.

---

## 2 · La regla que se desprende

**El criterio no es la distancia. Son tres pruebas, en este orden.**

### Prueba 1 · Continuidad de la red

Si los núcleos forman una red continua —vacíos cercanos a cero—, es **una** zona. Recoleta con
tres pares a 0,0 m no admite discusión.

Umbral de referencia empírico: **por debajo de unos 50 m, unir**. Es el rango donde vivían casi
todos los pares de Recoleta.

### Prueba 2 · Estabilidad de la partición

Barrer el umbral y contar componentes. **Si el número de partes cambia con un cambio chico del
umbral, la partición es arbitraria y se sube un nivel.**

Es la prueba que decidió Belgrano y es la más importante de las tres, porque es la que evita
publicar una división que sólo existe por el parámetro que elegimos. La curva 6-6-3-2-1 se
guarda y se publica: **una partición sin curva de sensibilidad no es defendible.**

### Prueba 3 · ¿La división mejora la lectura?

Recoleta: «la multiparte no mejora la lectura». Belgrano: tres centralidades con nombre propio y
reconocibles sí la mejoran.

Se responde con dos cosas concretas: **¿cada parte tiene nombre de uso corriente?** y **¿tiene
respaldo documental propio?** Belgrano R sobrevive con 2 locales por eso. Un fragmento sin
nombre y sin respaldo no es una parte: es ruido.

### Regla 4 · Toda decisión de unir se toma ENTRE PUNTOS

*Agregada el 6 de agosto de 2026, midiendo el saliente de P078.*

**La distancia entre envolventes se reporta al lado y no decide.**

El motivo no es una preferencia de método: es una propiedad del hull. El borde de una envolvente
es un segmento tendido entre dos puntos lejanos, y un tercer punto puede pasar cerca de ese
segmento **sin estar cerca de ningún punto real**. Por eso la distancia entre envolventes es
siempre menor o igual que la distancia entre puntos, y a veces mucho menor.

El caso que la hizo aparecer: el bloque mayor del saliente de P078 está a **11,3 m de la
envolvente** de P078 y a **55,8 m del punto más cercano**. Con la primera columna caía debajo del
corte de 50 m de Recoleta y se unía; con la segunda no llega. **Con la columna equivocada, P078
pasaba.**

Y no es una particularidad de P078. Sobre los 35 pares candidatos a unión
(`auditoria_uniones_por_envolvente.csv`):

| | |
|---|---|
| pares que cambian de lado del corte de 50 m según la columna | **7 de 35** |
| factor mediano entre las dos distancias | 1,2× |
| factor máximo | **7,4×** — P091+P088: 16,2 m de envolvente, **119,4 m entre puntos** |

Un par a 16 metros de envolvente y 119 entre puntos es, leído por la columna del hull, un caso de
unión obvia bajo el precedente Recoleta. Entre puntos está en la banda donde ni siquiera se
discute.

**Dónde sí sirve la distancia entre envolventes:** como filtro para elegir qué pares se evalúan.
Como es siempre ≤ que la distancia entre puntos, un filtro por envolvente peca de ancho y nunca de
angosto — deja pasar todo par que esté cerca entre puntos, más algunos que no lo están. Filtrar
con ella es seguro; decidir con ella no.

*Las dos uniones ya firmadas se reauditaron con este criterio y ninguna se recorre: se habían
decidido por continuidad y estabilidad, que corren sobre puntos. Lo que cambia es la cita —
P090+P089 está a **21,6 m** entre puntos y no a 15,1; P101+P099 a **85,2 m** y no a 85,1—.*

---

## 3 · La tabla, para aplicar a los 118

| separación entre núcleos | qué es | precedente |
|---|---|---|
| **0 – 50 m** | una sola zona, sin discusión | Recoleta (9 → 1) |
| **50 – 200 m** | depende de la estabilidad y del nombre. Partes de una zona si las partes tienen identidad; una sola si no | Belgrano (3 partes a 160 m) |
| **> 200 m** | zona multiparte con vacíos visibles, o zonas distintas | Costanera (163 – 2.727 m) |

Y una regla de tamaño mínimo por parte: **un componente de 1 o 2 locales no es una parte.**
Sobrevive sólo con respaldo documental que lo justifique.

---

## 4 · Qué significa esto para P072 y los 9 encadenados

P072 encadena Belgrano, Núñez y Colegiales: 440 ha a 3 locales/ha, y contiene entera a R05.

Aplicando las tres pruebas:

- **Continuidad.** Un encadenamiento a 3 locales/ha no es una red continua: es una cadena a
  través de corredores ralos. Hay que medir los vacíos entre sus núcleos como se hizo con
  Recoleta. Si son de cientos de metros, no es una zona.
- **Estabilidad.** Es la prueba decisiva. **R05 solo ya se descompone en tres a 160 m.** Un
  polígono que contiene a R05 entera y le suma dos barrios más casi seguro se descompone en
  varias piezas estables apenas se ajuste el umbral. Corré la curva.
- **Lectura.** «Belgrano–Núñez–Colegiales» no es un nombre que alguien use. Recoleta sí lo es, y
  por eso unir nueve núcleos ahí produjo algo nombrable. Acá produce algo que nadie sabría cómo
  llamar, que es la señal más clara de que no es una zona.

**Los diez encadenados se parten**, y se parten con la curva de sensibilidad publicada al lado,
no a ojo.

---

## 5 · Y al revés: dónde conviene unir entre los 118

Diego tiene razón en que estudiar menos zonas más grandes vale mucho. El precedente de Recoleta
lo habilita explícitamente —«unidad general más parsimoniosa»— y hay un lugar obvio donde
buscar: **los pares de polos cuya separación esté por debajo de 50 metros.**

Es un cálculo directo sobre el borrador: distancia mínima entre envolventes, para los 118 × 117
pares. Todo par por debajo de 50 m es candidato a unión inmediata bajo el precedente Recoleta.
Entre 50 y 200 m, van a la prueba de estabilidad.

**Ese cálculo es lo primero que haría con el borrador**, antes de enriquecer nada: si el número
de polos baja de 118 a algo del orden de 70 u 80 uniendo lo que está pegado, todo el trabajo
posterior se abarata y el mapa mejora.

---

## 6 · Lo que no cambia

- Ninguna zona publicada del Atlas se toca. Este criterio se aplica al **borrador**.
- La ambigüedad de fondo no se resuelve con un número: «polo gastronómico» es una categoría de
  lectura territorial, no una entidad natural. Lo que estas tres pruebas dan no es la verdad, es
  **una decisión reproducible y con precedente** — que es lo defendible.
- Y donde el criterio deje empatados dos caminos, gana el que se pueda nombrar. Es lo que hizo
  la Dirección en Recoleta y en Belgrano, y es el criterio correcto para un atlas.
