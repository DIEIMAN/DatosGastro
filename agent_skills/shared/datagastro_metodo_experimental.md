---
name: datagastro-metodo-experimental
description: Reglas para producir resultados que aguanten. Se aplica cada vez que una corrida, un cálculo o un experimento va a producir un número que después alguien va a leer como conclusión. Complementa datagastro-guardrails (que dice qué no hacer) diciendo cómo hacer.
---

# Método experimental · DataGastro

Estas trece reglas no salieron de un manual. Salieron de errores concretos de este proyecto, y
cada una tiene abajo el caso que la originó. Son duras: si una corrida no las cumple, su
resultado no se reporta como conclusión.

Las ocho primeras salieron de la fase de medición; **R9 a R13 salieron de la fase documental**, y
tienen un aire de familia entre sí: las cinco son sobre **cómo se atribuye un dato a un objeto** —
a una capa, a una fila, a una fecha, a una geometría, a una entidad.

---

## R1 · La lectura se escribe ANTES de correr

Antes de ejecutar, se declara por escrito **qué resultado significaría qué**. Bandas, umbrales de
decisión, y qué haríamos con cada uno.

```
0 – 15 %   → conclusión firme, el plan se replantea
15 – 60 %  → rango intermedio, decide una persona
60 % o más → la barrida era chica, el plan no se toca
```

Va en el código o en el prompt, no en la cabeza. Y **el veredicto lo elige el número**, no quien
lo lee.

> **De dónde salió.** La prueba de techo de Places sobre R08 dio 12,5 %, y el rango de robustez
> llegaba a 17,1 % — cruzaba dos bandas. Con las bandas escritas de antemano eso se reportó como
> rango. Sin ellas, se habría publicado la punta que convenía.

**Corolario:** si el resultado cae justo en un borde, se reporta el borde. No se corre el borde.

---

## R2 · Toda ablación lleva control aleatorio

Si se mide el efecto de quitar algo —una fuente, un filtro, un conjunto de puntos— hay que medir
también el efecto de quitar **la misma cantidad al azar**. Sin eso no se sabe si el efecto es de
lo que se sacó o de cuánto se sacó.

> **De dónde salió.** Sacar el Relevamiento de Usos del Suelo colapsaba el mapa de polos. Sacar
> la misma cantidad de puntos al azar, cinco veces, no lo colapsaba ninguna. Sin el control
> aleatorio, **tres de las cinco filas de la ablación se leían al revés.**

---

## R3 · Un umbral no se mueve para rescatar un caso

Los umbrales se fijan **una vez, para todo el universo, antes de mirar qué sobrevive**. Si al
aplicarlos un caso conocido desaparece, se anota como divergencia y se explica. **No se baja el
umbral para recuperarlo.**

Y se anclan afuera de los datos que van a juzgar: en un valor ya publicado, en un hueco natural
de la distribución, o en una convención declarada como tal.

> **De dónde salió.** El mínimo de tamaño para un polo se ancló en 40 locales porque es la zona
> publicada más chica del Atlas. Si hubiera salido de mirar el histograma de los clusters, el
> mapa habría confirmado lo que ya creíamos.

**Corolario sobre las convenciones.** Si un corte no corresponde a un hueco natural, se declara
como **convención**, no como frontera descubierta. Una convención declarada es defendible; un
corte óptimo presentado como natural se cae en la primera revisión.

---

## R4 · Si un resultado depende de un parámetro, se publica la curva

Cuando el resultado cambia con un parámetro elegido a mano, la corrida no está completa hasta
tener el **barrido**: el resultado a lo largo de un rango, con el conteo y los tamaños.

```
umbral_m  n_componentes  tamaños        pct_locales_en_esas_componentes
   80          6         5;5;2;2;2;1               —
  120          6         5;5;2;2;2;1               —
  160          3         8;7;2                     —
  200          2         8;9                       —
```

**Si el resultado es estable a lo largo del rango, eso es un hallazgo.** Si cambia, la elección
del parámetro es la mitad del resultado y hay que decirlo.

> **De dónde salió.** Belgrano se publicó con tres partes porque a 160 m emergen tres piezas de
> tamaño comparable. A 120 m aparecían seis, cuatro de ellas de tamaño 1 o 2. La decisión
> textual fue: «elegir cuatro sería arbitrario».

**Corolario.** «El método no lo partió» no es una conclusión. «Medimos que no tiene estructura
interna, con controles positivos que sí se partieron» sí lo es.

---

## R5 · Antes de gastar, el número

Ninguna llamada a una API paga se ejecuta sin **presentar antes la cantidad estimada de
requests, el piso, el techo y el saldo del período**. La autorización es sobre ese número, no
sobre la idea.

```
piso exacto                          24
estimación si B y C se comportan como A   117
tope duro autorizado                 150   (sin tolerancia, corta exacto)
franja del mes                       5.000 · gastados 256 · quedarían 4.594
```

El tope se implementa en el código y corta solo. Al terminar se reporta **gastado contra
estimado**.

Y antes de gastar: **mirar el disco.** Tres zonas que parecían tener faltante de cobertura no lo
tenían — el diagnóstico salió de datos que ya estaban, sin una sola llamada.

Y al gastar: **guardar los crudos tal como vinieron**, para que rehacer el análisis no vuelva a
costar. El corolario de R8.

---

## R6 · Cada dato lleva su procedencia y su licencia

Todo registro guarda **de qué fuente vino, con qué identificador en esa fuente, y bajo qué
licencia**. No se colapsan las fuentes a un registro «verdadero»: se guarda lo que dice cada una.

Y la licencia decide qué se publica:

| nivel | qué se publica | cuándo |
|---|---|---|
| `abierto` | registro completo | la identidad viene de una fuente redistribuible |
| `punto` | punto y categoría, sin nombre ni dirección | la ubicación está corroborada, la identidad no |
| `agregado` | sólo el conteo en una celda o zona | el dato existe únicamente en una fuente no redistribuible |

**Y las fuentes no siempre son independientes.** Overture incluye a Foursquare y a All The
Places: no son tres. Definí grupos de independencia y contá grupos, no fuentes, o la
corroboración deja de significar algo.

---

## R7 · No encontramos ≠ no existe

Es una regla de redacción y es la que más rápido se rompe.

| se escribe | no se escribe |
|---|---|
| «con la cobertura disponible, no se identificaron polos en el sur» | «no hay polos en el sur» |
| «la última señal de actividad es de 2023» | «el local está abierto» |
| «no figura en ninguna de las fuentes relevadas» | «no existe» |

> **De dónde salió.** El Atlas publicado dice «No se identificaron zonas en el extremo sur de la
> Ciudad». Es literalmente cierto y se lee como si no hubiera. El barrido posterior encontró
> diez polos con mil locales ahí. La frase no era falsa: era una afirmación sobre dónde
> habíamos mirado, escrita como una afirmación sobre el territorio.

**Corolario.** Cuando la ausencia de un resultado se pueda explicar por cobertura floja, **la
cobertura va al lado del resultado**, no en una nota al pie.

---

## R8 · Un campo pedido que vuelve vacío en el 100 % de las filas corta la corrida

Si la consulta pidió explícitamente un campo y ese campo viene nulo en todas las filas, no es un
dato faltante: es un **error de nombre, de esquema o de contrato**. La corrida aborta y avisa.
Nunca se reporta un resultado sobre un campo que llegó vacío entero.

> **De dónde salió.** Una consulta a Places pidió `places.types` en el FieldMask y el código leyó
> `primaryType`. Devolvió `None` en todas las filas, la corrida terminó bien, y el informe salió
> **sin rubro** — que era justo lo que había que medir. Costó **37 requests**.

Es la misma familia que el mojibake y que `esq` matcheando adentro de «Esquiu»: **falla en
silencio y parece dato.** Ninguno de los tres tira una excepción; los tres producen un resultado
que se explica bien con una hipótesis equivocada («Places no devuelve el rubro», «USIG no tiene
esa dirección»). Por eso no alcanza con que la corrida termine sin error.

**El patrón general, para el resto de los controles:** todo campo que el pipeline declare como
obligatorio **se verifica no nulo en al menos una fila antes de seguir.** Una fila alcanza — lo
que se está detectando es el campo que no llegó nunca, no el dato que falta a veces.

**Corolario, y es el que evita que el error cueste plata: adquisición y análisis van separados
cuando la adquisición se paga.** Los crudos se guardan tal como vinieron, y el informe se rehace
desde el disco con un `--solo-analisis` que no consulta nada. Así un error de lectura se corrige
gratis. **Es el estándar para toda consulta paga**, junto con el presupuesto duro de R5.

---

## R9 · Antes de reportar un dato como nuevo, se cruza contra la capa cargada

Nunca contra archivos propios. La pregunta no es «¿lo tenía yo anotado?», es «¿ya está en la
capa?».

> **De dónde salió.** Un insumo trajo diez establecimientos de Monserrat y marcaba nueve como
> ausentes de nuestra base. **Cinco ya estaban en la capa, con punto y con dirección** —Bar El
> Colonial, Bar Seddon, Cabildo, El Querandí y London City—: habían entrado con el canon del
> Boletín y con la Res. 1225/26. Darlos de alta habría creado cinco duplicados que inflaban
> exactamente la vía B que esa ronda estaba tratando de medir bien.

El cruce cuesta una línea de código. Un duplicado en una capa de hitos cuesta una vía abierta de
más, y no se nota hasta que alguien cuenta a mano.

---

## R10 · Un referente sin dirección no se carga en ninguna capa

Y todo nombre presente en dos capas lleva **marca explícita de par**.

Un referente sin dirección no es un dato incompleto: es un dato **inauditable**. No se puede
geocodificar, no entra en ninguna medición espacial, y no se puede cruzar contra nada — pero
ocupa una fila y se cuenta.

> **De dónde salió.** Dos casos distintos. La capa arrastra cinco hitos sin coordenadas, cuatro de
> ellos sin dirección, todos de `REFERENTES_2026`: existen en el conteo y no existen en ninguna
> medición. Y **Miramar estaba dos veces** —`H078` como Bar Notable en Sarandí 1190 y `ICO-012`
> como Restaurante Icónico en Av. San Juan 1999—, que es la misma ochava y el mismo local con
> doble reconocimiento oficial. Las dos filas se conservan, porque fusionarlas movería el conteo
> sin que se vea, pero quedan **apuntadas entre sí**.

---

## R11 · La fecha de un metadato no es la fecha del dato

Ni `metadata_modified`, ni fecha de actualización, ni fecha de publicación si el cuerpo es refrito.

> **De dónde salió.** Tres veces, en tres fuentes distintas. **FD-01**: `cronista.com` re-selló
> archivo entero con una misma fecha de actualización, incluida una nota que recomendaba dos
> restaurantes en una sede cerrada cinco meses antes. **FD-19**: dos fichas del GCBA con el mismo
> tono institucional, una editada el 20/02/2026 y otra inerte desde el 08/09/2021 — el texto no
> las distingue. Y **Places no trae fecha del dato**: devuelve un estado sin decir de cuándo es,
> así que la fecha de consulta la tiene que escribir quien consulta.

**Corolario operativo:** toda consulta a una fuente que no fecha su propio dato escribe la fecha
de consulta en la misma fila. Sin eso, en seis meses hay un campo del que no se sabe la añada.

---

## R12 · Toda delimitación se verifica midiéndola

Un tramo tiene que tener longitud. Y una contención se verifica por **superficie perdida**, no por
predicado.

> **De dónde salió.** Dos fallas silenciosas en la misma ronda. Una delimitación decía «Av.
> Rivadavia entre Boyacá y Carabobo», y **Boyacá y Carabobo son la misma avenida**, que cambia de
> nombre al cruzar Rivadavia: el tramo medía **cero cuadras** y la zona se quedaba sin perímetro
> sin que nada fallara. Y `covers()` de GEOS **devuelve `False` sobre geometrías cuya diferencia
> mide exactamente 0,0 m²** —falla de robustez de `relate` con vértices casi colineales—, así que
> un `assert` sobre el predicado habría abortado una corrida correcta, y su inverso habría dado
> por buena una que perdía superficie.

Las dos fallan sin tirar excepción, que es la familia de R8.

---

## R13 · Una atribución se verifica contra la entidad nombrada

No contra la más cercana en el texto, ni contra la más cercana en el mapa.

> **De dónde salió.** Una alarma decía que la zona de Barracas había perdido «su pieza más
> visible» y la atribuía a **El Puentecito**. La pieza era **Los Laureles**, a 1,5 km: El
> Puentecito nunca cerró. Y en el mismo período, el barrio de un Bar Notable se resolvió por
> **altura del callejero** y no por el nombre de la calle, que es lo que había puesto el catálogo:
> Café Olimpo estaba asentado en Villa Luro y el 1491 de Irigoyen es Monte Castro.

La proximidad —de un párrafo o de un punto— es una hipótesis de atribución, no una atribución.

---

## Antes de reportar un resultado, diez preguntas

1. ¿Estaba escrita la lectura antes de correr?
2. Si hubo ablación, ¿tuvo control aleatorio?
3. ¿Algún umbral se movió después de ver el resultado?
4. Si el resultado depende de un parámetro, ¿está la curva?
5. Si se gastó presupuesto, ¿se reportó gastado contra estimado?
6. ¿Hay alguna frase que diga «no existe» donde corresponde «no encontramos»?
7. ¿Algún campo que la consulta pidió llegó vacío en el 100 % de las filas?
8. ¿Esto ya existe en la capa cargada?
9. ¿La fecha que estoy usando es del dato o de su metadato?
10. ¿La relación que afirmo entre dos objetos está verificada, o inferida por proximidad?

Si alguna respuesta incomoda, el resultado todavía no es una conclusión.

---

## Qué hacer cuando un control falla

**No se elige otro control.** Se diagnostica por qué falló, se mide el diagnóstico, y se
reportan las dos lecturas.

> Cuando el índice de estabilidad de las clases de densidad dio 0,391 contra un umbral declarado
> de 0,60, las dos explicaciones intuitivas se midieron y las dos resultaron falsas. La
> explicación real —que el método de corte está dominado por la cola de la distribución— sólo
> apareció porque no se cambió el umbral.

Un control que falla y se reemplaza por otro más benévolo no es un control: es un trámite.
