# Ronda 14 · las seis mediciones de la tanda 5 · 2026-08-09

Seis tareas de medición, todas de geometría, ninguna de investigación.
**Google Places: 0 requests.** No se tocó el pipeline público, ni las láminas, ni la sección VII.

Trabajo en paralelo con Codex, que tiene el mapeo 124×42, el normalizador de calles y las curvas
de continuidad. **Nada de eso se toca acá**, y donde el borde estuvo cerca queda dicho.

Lo que sigue está ordenado por lo que más cambia una decisión, no por el orden de la tanda.

---

## 1 · La tarea que ya estaba hecha, y lo que apareció al rehacerla

**Las dos ampliaciones estaban medidas desde la ronda 7.** `geometria_r7/ampliaciones_r7.csv`,
`AMPLIACIONES_R7.txt` y `referencias_r7.geojson`, corridos el 08/08 con exactamente la misma regla
que pedía la tanda: unión con el viejo, buffer de 150 m, contención por superficie perdida. Los
polígonos ampliados viajaron a `referencias_r8.geojson` y son los que la capa usa hoy.

Es la **sexta vez** que el proyecto rehace algo que ya estaba hecho, y por la causa de siempre.
**ERR-16.**

> **Pero esta vez la repetición pagó, y conviene ser preciso sobre por qué.** La corrida se hizo
> desde el texto de las decisiones, sin abrir el resultado de la ronda 7 hasta tener números
> propios. Una de las dos reproduce exacto y la otra no — y la que no reproduce esconde un error
> de medición que, con el resultado de la r7 a la vista, nadie habría salido a buscar. **Eso es
> suerte, no método.**

### R21 La Paternal reproduce al centímetro

```
antes    321,01 ha ·  208 locales        (envolvente publicada)
después  385,34 ha ·  307 locales        +64,33 ha · +99 locales
ronda 7  385,34 ha ·  307 locales        REPRODUCE
capa r8  385,34 ha ·  307 locales        diferencia simétrica 0,0 m²
```

Las siete calles de la decisión 8 dan lo mismo resueltas de las tres maneras —nombre exacto,
columna de barrio, raíz canónica— porque ninguna está partida. **La ampliación de R21 ya está en
la geometría publicada desde la ronda 8**, y el 208 / 321,01 que cita la ficha es, correctamente,
el perímetro viejo.

### R19 Federico Lacroze no reproduce, y la diferencia tiene nombre y apellido

```
ronda 7    303,28 ha ·  532 locales
corregido  354,10 ha ·  603 locales      +50,82 ha · +71 locales
```

La ronda 7 buscó cada eje por su **nombre exacto** del callejero. Dos de los cuatro están partidos
en dos nombres oficiales:

| calle | r7 · nombre exacto | raíz canónica + polígono | lo que se perdió |
|---|---:|---:|---|
| FRAGA | 1.492 m | 1.492 m | — |
| CHARLONE | 1.536 m | 1.536 m | — |
| **DORREGO** | 2.498 m | **3.159 m** | `DORREGO` sin el `AV` |
| **NEWBERY JORGE** | 1.309 m | **3.320 m** | `NEWBERY JORGE AV`: más de la mitad del eje |

**No es un descuido de la ronda 7.** `callejero_canonico.py` —el módulo que resuelve exactamente
esta familia— se escribió en la **ronda 10**, tres rondas después. Son el cuarto y el quinto caso
de la misma propiedad del callejero, después de ESQUIÚ, INDEPENDENCIA y GARCÍA DEL RÍO. **ERR-14.**

> **Y hay una segunda trampa que esta corrida sí se comió, en su primera pasada.** Filtrar los ejes
> por la **columna** `barrio` en vez de recortarlos contra el **polígono** del barrio pierde los
> tramos donde la calle *es* el límite: Dorrego cae de 3.159 m a 1.573 m, la mitad. La ronda 7 ya
> lo sabía y por eso recortaba contra el polígono. Cada corrida cayó en una trampa distinta.

### La contención: 0,0000 m² las dos veces, con el predicado en contra las dos veces

```
R19   superficie del viejo que queda afuera:  0,0000 m²   ·  covers() dice False
R21   superficie del viejo que queda afuera:  0,0000 m²   ·  covers() dice False
```

**Van siete mediciones contra cero.** Palermo en la ronda 10, las cuatro decisiones de geometría de
la ronda 7 —R18, R19, R20 y R21— y las dos de esta corrida: en las siete la superficie perdida da
0,0 m² y en las siete `covers()` dice que no. Ya no es una anécdota de GEOS: es la manera de medir
contención en este proyecto.

Y la prueba no es vacía aunque el polígono nuevo se construya como unión con el viejo: lo que
puede comerse superficie no es la unión, es la **reparación** — `buffer(0)` sobre una geometría
inválida descarta lo que no puede resolver y no avisa.

### Lo que la ampliación de R19 le hace a la fusión

R19 ya no existe como referencia independiente. Medida contra `R09R19_CHACAGIALES`:

```
el 92 % de la ampliación corregida ya está adentro de la fusión
lo que sobra:  27,57 ha · 62 locales · en 17 piezas
```

**Diecisiete piezas para 27 hectáreas es un fleco, no una zona nueva.** La ampliación corregida no
agrega territorio coherente a Chacagiales: le agrega borde.

---

## 2 · Colegiales · la franja que se pidió trazar está afuera de Colegiales

La ronda 9 ya había medido que **Av. Álvarez Thomas y Av. Forest se encuentran a 0 m** y que de las
cuatro calles de la lista sólo dos tienen tramo verificable —Zabala 254 m y Virrey Avilés 344 m—.
Trazado sobre eso, aparecen dos cosas más.

### No hay una cuña: hay dos, y no se tocan más que en un punto

Las dos avenidas no confluyen y terminan: **se cruzan**, en un único punto, y dejan cuatro
sectores. Zabala cierra el del sudeste y Virrey Avilés el del noroeste.

| cara | ha | locales | perímetro | ancho del corte | barrio |
|---|---:|---:|---:|---:|---|
| cerrada por **Zabala** | 3,66 | 5 | 878 m | 253 m | **Chacarita 100 %** |
| cerrada por **Virrey Avilés** | 3,34 | 12 | 980 m | 363 m | **Villa Ortúzar 100 %** |

```
superficie común entre las dos caras:  0,00 m²
distancia entre las dos caras:         0,00 m
```

**Se tocan en el ápice y en ningún otro punto.** La «franja» no es una banda continua: es un moño.

### Y ninguna de las dos está en Colegiales

**Ni un metro cuadrado.** No es un error de la medición: Av. Álvarez Thomas y Av. Forest **son** el
límite del barrio, así que lo que queda entre las dos está por definición del otro lado. **ERR-15.**

Por eso se midió también la otra lectura, que es la que dice la fuente —Canal 26 nombra a esas
calles **«del lado de Colegiales»**—:

```
lectura A · "entre Álvarez Thomas y Forest", al pie de la letra
              6,99 ha ·  17 locales  ·  0 % en Colegiales

lectura B · las cuatro calles DENTRO del barrio, al buffer declarado de 150 m
            137,78 ha · 287 locales  ·  el 60 % del barrio
```

Y la lectura B tiene el problema opuesto: **la fuente no nombra el borde de adentro**, así que la
profundidad de la banda la pone el buffer y no la evidencia. **Ninguna de las dos es la franja que
el documento imagina**, y la B casi no resuelve lo que venía a resolver: el barrio entero aporta
229,08 ha y 441 locales, y la banda se lleva 137,78 y 287.

Con la cuña en lugar del barrio, Chacagiales pasaría de **495,82 ha / 891 locales** a **343,53 ha /
598 locales**. Es la magnitud que `COLEGIALES_NO_ES_UNA_COSA.md` anticipaba sin poder calcular.

### El Mercado de Pulgas está a 1,2 km de todo esto

La propuesta lo suma «aparte del eje». Sus dos anclajes —Gral. E. Martínez 50 y la esquina de
Dorrego y Álvarez Thomas— **coinciden entre sí a 144 m**, o sea que la propuesta lo ubica bien; pero
los dos quedan a **1.219 m y 1.268 m** de la franja medida. Los dos están dentro de Chacagiales
publicado. **Son dos objetos, no uno.**

### Una trampa nueva de shapely, la quinta de la serie

La cara de Virrey Avilés no cerraba: `polygonize` devolvía **cero caras, sin error**. La causa es
que el conector que empalma el eje con la avenida —los 16 m del empalme en T— termina en un punto
calculado en punto flotante que queda a **1,8 × 10⁻¹⁰ m** de la avenida. El noding de `unary_union`
es exacto: con ese hueco no crea nodo y no hay anillo. Se resuelve sobrepasando 1 m para que el
conector **cruce** en vez de tocar. **Es la misma familia que `covers()`: predicados exactos sobre
coordenadas que no lo son.**

---

## 3 · Av. Montes de Oca · abre cuatro vías, y su polígono es la mitad del corredor que anuncia

Medida como cualquier zona nueva, sobre **P066** de la capa de las 124 —18,02 ha, Barracas—.
**No sobre P008**: ese id designa dos cosas distintas según qué archivo se abra y es ERR-11, que
sale del mapeo que está haciendo Codex. P008 son 49 locales sobre Vieytes, Iriarte y California:
medirlo creyendo que es este corredor habría devuelto números perfectamente formados de otro objeto.

| vía | veredicto | lo que la sostiene |
|---|---|---|
| **A** densidad y continuidad | **abre** | 3,44 loc/ha · pero ver la salvedad |
| **B** trayectoria | **abre** | 6 hitos en Barracas · 1 dentro del polígono |
| **C** mercados y centralidades | no abre | el más cercano, el Mercado de San Telmo, a 1.515 m |
| **D** comunidades | no abre | el enclave más cercano a 6.253 m |
| **E** reconocimiento externo | **abre** (documental) | la declara la ficha; el repositorio no mide esta vía |
| **F** corredor | **abre** | elongación 2,45 sobre un corte de 2,0 |

**Tres de las cinco medibles, más la E. Cuatro vías.**

**La salvedad de la vía A, que es grande:** la regla de apertura es «algún polo del borrador con
≥50 % de sus locales dentro del soporte», y **el soporte ES un polo del borrador**. Se cumple sola.
Lo que informa de verdad es la continuidad, y no es buena: **a 60 m sólo el 24,2 % de los locales
está en la componente mayor**, y hace falta llegar a 120 m para que sea el 100 %.

### Los referentes de la ficha caen afuera del polígono

| establecimiento | distancia a P066 |
|---|---:|
| Los Campeones (Montes de Oca 856) | **dentro** |
| La Flor de Barracas | 523 m |
| Caseros (MICHELIN) | 707 m |
| **El Progreso** (Bar Notable, Montes de Oca 1700) | 760 m |
| **Los Laureles** (Av. Iriarte 2290) | 1.179 m |
| **El Puentecito** (Vieytes 1895) | 1.761 m |

### Y el número que lo explica

**El polígono cubre Av. Montes de Oca del 301 al 999 — 761 m de avenida adentro. La ficha anuncia
oferta documentada del 280 al 1702.**

```
la cuadra del  280   está a   63 m del polígono (afuera)
la cuadra del 1702   está a  771 m del polígono (afuera)
```

Por eso El Progreso, que está en el 1700, queda a 760 m: **no está lejos del corredor, está lejos
del polígono**, que es la mitad corta del corredor que la ficha describe. La ficha ya declara que
«la continuidad del corredor no está medida» y la llama su afirmación más expuesta; esto es un
hallazgo distinto y previo — **el polígono publicado y el corredor declarado no tienen el mismo
largo**.

> **Esto NO es la curva de continuidad**, que la está haciendo Codex. Es qué alturas cubre el
> polígono. La columna de continuidad que aparece arriba es la de la vía A, medida sobre la nube de
> puntos.

Y de paso, **dos confirmaciones del bug que Codex está arreglando**: el callejero escribe la
avenida «MONTES DE OCA, MANUEL AV.», así que buscarla como «Montes de Oca Av.» devuelve vacío sin
tirar error —el bicho R8 del orden de los tokens—; y `POLOS_NOMBRADOS.csv` publica como calles
dominantes de P066 «Montes De Oca (9); Manuel Montes De Oca (2)», que es la misma avenida contada
dos veces.

---

## 4 · La vía E · cierran 6 de los 10, no los 10

El cruce estaba bien planteado —la zona ya tiene veredicto, sólo falta decir en cuál cae cada
polígono— y aun así **cuatro de las diez no se pueden cerrar por geometría**, por dos razones que
son la misma: *el polígono de la zona candidata no es una delimitación*.

```
base       79/94  (84 %)   ← el 84 % del tablero: filas con veredicto sí/no
con esto   85/94  (90 %)
si hubieran cerrado las 10   89/94 (95 %)
```

**Las seis que cierran son todas de Flores** y heredan de Z23 «no abre». **Las cuatro que no:**

| fila | por qué |
|---|---|
| **PGF2_FLORES** | el soporte es el barrio entero y **contiene** a Z24 y a Z39b. Heredar de una de ellas sería atribuirle al todo lo de una parte — la regla «la herencia no vale hacia arriba», leída al revés |
| **PGR_P107** · **PGR_P055** | ganan Z35 con 82,5 % y 100 %… pero **el polígono de Z35 es el barrio de Balvanera**. «Cae en Z35» y «cae en Balvanera» son la misma frase: no discrimina contra Z36 Congreso, que es la otra mitad de la pregunta y **no tiene polígono** — la ronda 8 la fusionó en Z47, cuyo polígono es el barrio de Monserrat |
| **PGR_P085** | Z35 43 % · Z47 23 %. Ninguna llega al 50 % |

> **Las dos reglas que descartan esas cuatro se agregaron DESPUÉS de la primera pasada, que cerró
> 9 de 10.** Dos de esas nueve eran artefactos del instrumento: números ciertos que no significan
> nada. Se escriben en el encabezado del script en vez de corregir el resultado en silencio.

**Y una salvedad que viaja con las seis que sí cierran:** Z23 no es una delimitación, es un
**residuo** —«el barrio de Flores menos Z24 y Z39b»— y por lo tanto se traga Bajo Flores, cuya vía E
la ronda 2 le atribuyó a Z39, que **sí abre**. Heredar de un residuo es heredar de «lo que sobró».
El caso donde eso muerde es **PGR_P014**: 80,6 % en Z23 y 19,4 % en Z39, y la nota del archivo dice
que está rotulado «Bajo Flores» en el borrador. **Si lo es, hereda «abre» y no «no abre».**

---

## 5 · Los dos ejes del IDECBA, atribuidos · y escritos en el archivo

Los tramos se construyeron **como geometría** —las cuadras del callejero cuyo rango de alturas se
solapa con el del tramo— en vez de cruzar nombres de calle. Es el pendiente 4 de la ronda 13,
hecho para dos ejes.

### Triunvirato → R17 Villa Urquiza

| tramo | cuadras | metros | dentro | % |
|---|---:|---:|---:|---:|
| Av. Triunvirato 3601-4699 | 15 | 1.635 | 1.091 | 67 % |
| Monroe 4801-5399 | 9 | 823 | 823 | **100 %** |
| **el eje** | | **2.458** | **1.914** | **78 %** |

**Se atribuye.** Y el reverso dice lo que la propia ficha de R17 venía diciendo: **la banda de 150 m
del eje cubre sólo el 13 % del polígono, 162 de sus 528 locales.** El eje está adentro; R17 es siete
veces más grande que él.

### Avellaneda → Z24 Flores · Avellaneda y Ruperto Godoy

| tramo | cuadras | metros | dentro | % |
|---|---:|---:|---:|---:|
| Avellaneda 2701-3799 | 11 | 1.298 | 677 | 52 % |
| Bogotá 2901-3499 | 6 | 689 | 469 | 68 % |
| Aranguren 2901-3499 | 6 | 691 | 400 | 58 % |
| **el eje** | | **2.678** | **1.545** | **58 %** |

**Se atribuye**, y acá el encaje es de verdad: la banda del eje cubre el **55 %** de Z24, 41 de sus
107 locales. Son dos objetos del mismo tamaño. **Con una salvedad:** casi la mitad del eje relevado
—el más denso de los 48, con 23,33 locales por cuadra— **cae fuera del polígono publicado de Z24**.

Los dos cambios **están escritos en `ronda_12/idecba_48_autoridad.csv`**, no sólo registrados: es el
modo de falla que la ronda 12 y la 13 encontraron dos veces. **Los ejes atribuidos pasan de 27 a 29
de 48.**

---

## 6 · ERR-12 · Defensa 695 no puede ser de los dos, y el catálogo no estaba mal

```
BAR SEDDON     Defensa 695, esquina de CHILE       Monserrat   · dentro de Z47
BAR BRITANICO  Brasil 399, esquina de DEFENSA      San Telmo   · dentro de R11
                 el callejero pone ese cruce en Defensa 1499/1501
distancia entre los dos:  1.045 m
```

**Las dos filas de `catalogo_90_estado_final.csv` son correctas y no se tocan.** El error vivía en
un solo campo: la dirección del Británico en `ronda_13/verificaciones_seis_fichas_r13.csv`, que
decía «Defensa 695 esq. Brasil 399» — una altura de Monserrat con una esquina de San Telmo.

Resuelto con las dos fuentes que el proyecto ya tiene en disco: el dataset de Notables con
**geocodificación USIG del GCBA**, y el **callejero oficial** cuadra por cuadra, que pone la altura
695 en la cuadra 601-695 entre México y Chile, y a Brasil cruzando Defensa entre el 1499 y el 1501.
El punto del Seddon está a **3 m** de su cuadra; el del Británico a **24 y 25 m** de las dos cuadras
que hacen esa esquina.

**El veredicto de R11 no cambia:** el Británico cae dentro de R11 y la fuente que lo cierra sigue
siendo la misma. La corrección está aplicada en el CSV de la ronda 13; **las dos fichas de la
sección VII no se tocan desde el repositorio** — les corresponde a quienes las escriben sacar la
salvedad que las dos declaran.

> **Y una coincidencia que vale mirar dos veces.** El Británico está en la esquina de Defensa y
> Brasil, es decir **exactamente en el 1499/1501**: el número donde el eje Defensa del IDECBA
> termina (1499) y donde R11 empieza (1501). El único hito de R11 está parado sobre la bisagra de
> los dos números que la ronda 13 encontró que no se superponen.

---

## Lo que queda para Diego

1. **ERR-14 · adoptar o no las 354,10 ha y 603 locales de R19**, y decidir qué pasa con la
   ampliación adentro de la fusión Chacagiales, donde el 92 % ya está y lo que sobra son 27,57 ha
   en 17 piezas.
2. **ERR-15 · cuál de las dos lecturas de la franja de Colegiales** —6,99 ha fuera del barrio, o
   137,78 ha que son el 60 % de él— y si el Mercado de Pulgas entra como pieza aparte.
3. **ERR-13 · renumerar uno de los dos ERR-11.** La recomendación está en la errata.
4. **PGR_P014 · ¿es Bajo Flores?** Es la única de las seis que cierran cuya vía E cambia de «no
   abre» a «abre» según la respuesta.
5. **Las tres de Balvanera** no cierran hasta que Z36 Congreso tenga un perímetro propio dentro de
   Balvanera. Hoy no lo tiene y por eso el cruce no puede.
6. **Av. Montes de Oca:** el polígono publicado cubre del 301 al 999 y la ficha anuncia 280–1702.
   Hay que decidir si se amplía el polígono al corredor declarado o si la ficha cita el tramo del
   polígono — **hoy son dos objetos de distinto largo con el mismo nombre.**
7. **ERR-16 · el punto 6 del tablero** ya estaba hecho desde la ronda 7. El tablero es de Cowork.

**Y una para el repositorio, que sale de esta tanda:** los otros 46 ejes del IDECBA se pueden
construir como geometría con el mismo procedimiento de la tarea 5. Es lo que saca del punto ciego a
los 12 ejes que la sonda de nombres no puede ver.
