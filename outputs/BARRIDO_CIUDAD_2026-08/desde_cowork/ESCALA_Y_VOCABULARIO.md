# La escala del mapa, y qué llamamos polo

**6 de agosto de 2026** · Replantea el borrador de 124 después de dos definiciones de Diego: **las
22 publicadas se mantienen y sólo se amplían**, y **unos pocos locales no son un polo**.

---

## 1 · El problema, medido

No es una impresión. El borrador y lo publicado son objetos de escalas distintas:

| | las 22 publicadas | los 124 del borrador |
|---|---:|---:|
| zonas | 22 | 124 |
| **hectáreas · mediana** | **130** | **13** |
| **locales · mediana** | **330** | **65** |
| densidad · mediana | 2,14 loc/ha | 3,9 loc/ha |
| superficie total | 3.895 ha | 3.143 ha |

**Una zona publicada tiene diez veces el área y cinco veces los locales de un polo del borrador.**
La superficie total es parecida —de hecho el borrador cubre menos— pero repartida en cinco veces
más piezas. Eso es exactamente lo que se ve en el mapa: confeti.

Y hay algo más de fondo: **la unidad de las 22 no es un clúster, es «el área gastronómica de un
barrio»**. Catorce de las veintidós se llaman como un barrio o como una parte de un barrio.
Estábamos produciendo un objeto distinto del que el Atlas ya usaba.

## 2 · La escala, calibrada · no elegida por gusto

Se probaron reglas de agrupamiento sobre los 124 y se midieron contra la referencia. La regla
tiene que reproducir la escala publicada, no parecerse a ella de ojo:

| regla | zonas | ha mediana | locales mediana | ha total |
|---|---:|---:|---:|---:|
| tal como está | 124 | 13 | 65 | 3.143 |
| mismo barrio, hasta 600 m | 50 | 62 | 144 | 4.259 |
| mismo barrio, hasta 900 m | 45 | 66 | 161 | 4.259 |
| **mismo barrio, hasta 1.500 m, mínimo 120 locales** | **29** | **99** | **296** | **3.720** |
| libre hasta 300 m, mínimo 120 locales | 14 | 124 | 292 | 3.734 |
| **las 22 publicadas** | **22** | **130** | **330** | **3.895** |

**La regla de «mismo barrio» es la que da en el blanco**, y no es casualidad: es la unidad que el
Atlas venía usando. Veintinueve zonas con mediana de 99 ha y 296 locales es, a todos los efectos,
la misma escala que 22 zonas con 130 ha y 330 locales.

Y confirma la intuición de Diego palabra por palabra: **si durante unas cuadras hay muchísimos,
frena un poco y después sigue, es el mismo polo** — siempre que no cambie de barrio.

### La calibración contra los tres precedentes

Una regla de escala se valida contra las decisiones que ya se tomaron:

| precedente | qué se publicó | qué da la regla |
|---|---|---|
| **Recoleta** · 9 núcleos | una zona | **una zona** ✓ |
| **Belgrano** · 3 partes | una zona, familia «Polo» | **una zona** ✓ |
| **Costanera Norte** · 4 partes | cuatro, con los vacíos preservados | **una zona** ✗ |

**Costanera no la reproduce, y eso hay que decirlo, no esconderlo.** Sus vacíos miden 163, 462,
692, 1.418, 1.995 y 2.727 metros, y la decisión de preservarlos tuvo un motivo propio: entre parte
y parte hay río y parque, no tejido ralo. **Es una excepción con motivo documentado**, no un fallo
de la regla — y como excepción se declara y se conserva la multiparte.

## 3 · La arquitectura de dos capas

Es la consecuencia directa de que las 22 se mantengan.

**Capa A · las 22 publicadas.** Su perímetro **no se redefine**. Lo único que puede pasarles es
**ampliarse**, y sólo donde la medición muestra que la actividad se extiende más allá del
perímetro. Ya tenemos el caso medido: **279 de los 585 locales de la concentración de Palermo
Hollywood —el 47,7 %— caen fuera del perímetro de R01.** Ese es el tipo de ampliación que
corresponde, y va con su número.

**Capa B · las zonas nuevas.** Se construyen a la escala de la capa A, con la regla de barrio, y
**sólo donde no hay ya una zona publicada encima**. Hoy son **62 de los 124 polos los que no
tienen ninguna zona publicada arriba, con 4.678 locales** — ése es el territorio que la capa B
tiene que cubrir, y es donde está todo el sur y el oeste.

**Lo que no puede pasar:** que una zona nueva se superponga a una publicada y compitan. Si una
concentración nueva toca una zona publicada, o la amplía (capa A) o se descarta; no se publica al
lado.

## 4 · Qué llamamos polo · el vocabulario

Hoy «polo» nombra por igual a Palermo Soho, con 728 locales, y a una esquina con 40. **Eso vacía
la palabra**, y es lo que Diego marcó: unos pocos lugares no son un polo.

Tres nombres, con el corte anclado afuera de los datos, como corresponde:

| se llama | qué es | ancla del corte |
|---|---|---|
| **Polo gastronómico** | concentración con cuerpo, nombrable, que se camina | **≥ 120 locales** — la zona más chica de familia «Polo» del Atlas publicado tiene 71; 120 es el corte que deja la mediana nueva en la escala publicada |
| **Corredor gastronómico** | actividad tendida sobre una avenida, sin centro | forma alargada, no tamaño |
| **Área con actividad gastronómica** | presencia real, sin concentración que la explique | todo lo que no llega |

**La tercera categoría no es un descarte: es información y va publicada.** Es lo que evita que
«no es polo» se lea como «no hay nada», que es el error que este trabajo viene corrigiendo desde
el principio. Las concentraciones que hoy quedan entre 40 y 120 locales **no desaparecen del
Atlas**: cambian de categoría y siguen en el mapa, con su conteo.

**Y el mínimo de 40 no se movió, se jubiló.** Sigue siendo el piso para *entrar al relevamiento*.
Lo que se agrega arriba es un corte distinto, para una palabra distinta. No es lo mismo bajar un
umbral para rescatar un caso —que está prohibido— que declarar una categoría nueva con su propio
corte anclado.

## 5 · Y sobre la estética, que no es un capricho

Un mapa con 124 manchas chicas no se lee, no se presenta y no se usa para decidir nada. Un mapa
con unas 30 zonas con cuerpo se mira una vez y se entiende.

La forma también importa: los polígonos actuales se cierran con un hull ajustado. Cerrarlos con
una operación de **cierre morfológico** —engordar, unir, desengordar— da bordes más llenos y
menos astillados **sin inflar el área total**: en las pruebas, la superficie total se mantuvo en
~4.265 ha en todos los umbrales, mientras que el hull convexo la llevaba a 14.000, que es media
Ciudad y es absurdo.

Esto no contradice el método. **La escala del mapa es una decisión declarada, no un resultado
medido** — y como toda decisión de este proyecto, va con su curva al lado, su calibración contra
los precedentes y su excepción documentada.

---

## 6 · Agrupar no es lo mismo que verse agrupado · el radio de cierre

Al renderizar la primera prueba apareció algo que los números no mostraban: **agrupar 124
polígonos en 29 grupos no hace que el mapa se vea con 29 zonas.** Si las piezas de un grupo
quedan separadas, el mapa sigue leyéndose como confeti aunque la tabla diga 29.

Lo que cierra los huecos es una **operación de cierre morfológico** —engordar, unir,
desengordar— y su radio es un parámetro más, con su curva:

| radio de cierre | zonas | **piezas visibles** | ha mediana | ha total |
|---:|---:|---:|---:|---:|
| 90 m | 29 | 69 | 79 | 3.119 |
| 150 m | 29 | 55 | 86 | 3.436 |
| 250 m | 29 | 44 | 107 | 4.007 |
| **350 m** | **29** | **37** | **129** | **4.598** |
| 450 m | 29 | 35 | 149 | 5.257 |
| *referencia · 22 publicadas* | *22* | — | ***130*** | *3.895* |

**A 350 metros la mediana da 129 hectáreas contra las 130 publicadas.** No se buscó ese número:
se barrió el parámetro y ahí cayó. Y el mapa pasa de 124 manchas a 37 piezas visibles, que es la
diferencia entre un mapa que no se lee y uno que sí.

**Lo que cuesta:** el área total sube a 4.598 ha contra 3.895 de lo publicado, un 18 % más. Parte
de eso es cobertura real —el borrador cubre toda la Ciudad y lo publicado no— y parte es el
relleno del cierre. **Es el precio declarado de la escala**, y conviene tenerlo escrito antes de
que alguien lo mida.

**Un residuo honesto:** un radio de cierre de 350 m mete adentro del polígono manzanas que no
tienen ningún local relevado. En una zona con cuerpo eso es correcto —un polo tiene calles
internas sin oferta— pero hay que decir que el polígono es **la envolvente de la concentración, no
la lista de sus locales**. Ya está escrito así en los criterios de lectura.
