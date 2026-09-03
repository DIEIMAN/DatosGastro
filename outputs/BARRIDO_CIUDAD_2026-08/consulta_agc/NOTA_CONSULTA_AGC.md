> # ⚠ NO ENVIADA · decisión de alcance del 2026-08-06
>
> **Esta consulta quedó preparada y no se envió**, por la decisión de no hacer pedidos fuera de la
> Dirección. No está pendiente de nadie ni esperando respuesta: está dada de baja.
>
> Se conserva completa y sin modificar porque el trabajo de identificar el patrón y redactar la
> pregunta ya está hecho, y porque **la pregunta sigue abierta**: el criterio de carga de las
> habilitaciones asociadas a una misma partida matriz sigue admitiendo dos lecturas y nosotros
> seguimos sin saber cuál corresponde.
>
> Consecuencia declarada, no pendiente: el 22,6 % de asientos replicados se sigue tratando con el
> criterio propio adoptado, documentado en la prueba catastral, **sin confirmación del organismo
> que los publica**. Eso va escrito donde se use ese número.
>
> Si alguna vez la decisión de alcance cambia, la nota está lista para salir tal como está.

---

# Consulta técnica sobre la carga de habilitaciones asociadas a una misma partida matriz

**Dirección General de Desarrollo Gastronómico**
**Destinatario:** Agencia Gubernamental de Control

---

## 1. Objeto

Elevamos una consulta técnica sobre el criterio de carga del padrón de habilitaciones publicado en
BA Data. Trabajando sobre el universo gastronómico encontramos un patrón regular que admite dos
lecturas, y antes de fijar un criterio propio preferimos preguntar cuál corresponde.

No se trata de una observación sobre la validez de las habilitaciones ni sobre ningún trámite en
particular. La consulta es sobre cómo debe interpretarse la unidad de registro del dataset.

## 2. El patrón observado

Al agrupar el padrón por dirección aparecen 137 direcciones, en 20 barrios, que
concentran 9.697 registros de habilitación: entre 21 y 144 registros por número de puerta.
Se agrupan en 45 conjuntos que comparten cuatro rasgos:

- números de puerta consecutivos de una misma cuadra;
- la misma cantidad de registros y la misma mezcla de rubros en cada dirección del conjunto;
- ausencia de fecha de habilitación en la totalidad de los registros;
- **la misma partida matriz para todas las direcciones del conjunto.**

A modo de ejemplo, sobre la Av. Ramón L. Falcón al 7100 figuran 15 números de puerta
(7115, 7119, 7121, 7123, 7129, 7131, 7135, 7137...), cada uno con la misma composición de rubros, todos bajo la misma partida matriz
(94035).

## 3. Cómo lo leemos, y por qué preguntamos

Nuestra lectura es que **no se trata de un local por número de puerta, sino de un inmueble único
cuyos permisos quedan asentados contra cada número del frente de manzana**.

**El mecanismo está a la vista en el propio padrón.** En los archivos de 2015 a 2024, el campo
`calles` admite varios números de puerta en un mismo registro: `PUEYRREDON AV. 460;PUEYRREDON AV.
468` es un asiento, no dos. Tiene más de un número el 13,9 % de los registros, y figuran con más de
una puerta 15.237 de 42.246 parcelas (36,1 %); el máximo observado es de 237 números en una sola
parcela. Es decir: el padrón asienta el frente completo del inmueble.

La cohorte 2025 —donde aparecen estos conjuntos— no incluye ese campo, sino un domicilio por fila.
Al normalizar de una forma a la otra, cada número del frente pasa a comportarse como una dirección
independiente. Eso da cuenta del patrón descripto en la sección 2 sin necesidad de suponer un error
de carga.

**El catastro corrobora.** Los archivos de 2015 a 2024 incluyen sección, manzana y parcela.
Cruzando por partida matriz, las 37 partidas involucradas resuelven todas a una única parcela
catastral. La partida 223955 —parcela 1-32-2B en notación sección-manzana-parcela— reúne 75 números
de puerta sobre cuatro calles (Florida, Córdoba, Viamonte y San Martín): una manzana completa.

Corresponde precisar cuánto pesa esa corroboración. En el padrón, el 99,26 % de las partidas
resuelve a una sola parcela, de modo que el dato sólo es informativo comparado contra partidas de
tamaño equivalente en cantidad de direcciones. Entre las partidas con 11 o más números de puerta
sólo el 42,5 % resuelve a una única parcela; las 5 de ese grupo que aparecen en estos conjuntos
resuelven todas a una, y ahí el cruce sí distingue. En cambio, entre las partidas de 2 direcciones
la proporción es del 99,6 %: para las 20 de nuestro conjunto que están en ese caso, el resultado es
consistente con nuestra lectura pero no la distingue de ninguna otra. Lo señalamos para no
atribuirle al catastro más fuerza de la que tiene; el peso del argumento está en el mecanismo.

Adicionalmente, sobre las direcciones de estos conjuntos, 23.694 registros se reducen a 658
combinaciones distintas de titular y rubro.

**La consulta concreta es:** ¿este patrón responde a un criterio de carga por frente de manzana o
por unidad funcional del inmueble, previsto por el régimen de habilitaciones? ¿O corresponde
interpretarlo como una duplicación de asiento?

Formulamos la pregunta en estos términos porque no podemos descartar que se trate de una
convención registral correcta que estamos leyendo con una unidad de análisis equivocada.

## 4. Por qué puede interesarles más allá de nuestro trabajo

El dataset es de publicación abierta. Cualquier usuario que cuente registros por dirección —o
direcciones por barrio— sobre estas zonas obtendrá volúmenes que no se corresponden con la cantidad
de establecimientos. En nuestro universo el efecto alcanza al 22,6 % de los registros
georreferenciados, concentrado en unas pocas cuadras del centro y del oeste.

En nuestro caso está resuelto: estas direcciones quedan fuera del conteo por una regla previa, de
modo que ninguna cifra que hayamos publicado está afectada. Lo señalamos porque el mismo dato, leído
sin esa precaución, es fácil de contar mal.

## 5. Anexo

`anexo_consulta_agc.csv` — 137 direcciones con su partida matriz, clave catastral SMP,
barrio y cantidad de registros asociados.

El anexo contiene únicamente identificación catastral y domiciliaria del inmueble. **No incluye
razón social, CUIT, teléfono ni datos de titulares.** Si para la verificación resultara necesario
identificar trámites concretos, la partida matriz permite ubicarlos en el sistema de la Agencia.

---

**Fuente:** habilitaciones aprobadas, publicadas en BA Data (cohortes 2015-2018, 2019 a 2024 y
2025). Universo de análisis: rubros gastronómicos.

---

## Addenda de estado · 2026-08-27

La decisión del 6 de agosto de no realizar pedidos fuera de la Dirección fue **superada por una
nueva decisión de Diego**. La consulta técnica vuelve a estar habilitada, pero no debe enviarse de
forma aislada ni con la redacción histórica como único pedido.

El pedido vigente parte de la revisión de los recursos públicos de AGC, incluido el recurso 2026,
y solicita una reunión sobre el estado actual de las autorizaciones, los identificadores de enlace
y la historia administrativa. Esta nota se conserva como **anexo técnico específico** sobre la
unidad de registro y las múltiples puertas por partida.

Borrador vigente:
`docs/polos_gastro/pedidos_institucionales_padron_2026-08-27/BORRADOR_PEDIDO_AGC.md`.
