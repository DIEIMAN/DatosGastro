# Ronda 2 · la evidencia cargada, el ENTUR y los ejes comerciales · 2026-08-07

Cierra los tres huecos de fuente que la ronda 1 dejó a la vista y baja las dos fuentes que desde
afuera no se podían abrir. **Google Places: 0 requests.** USIG sí. Ninguna geometría publicada
tocada. La lectura estaba escrita antes de correr, en `LECTURA_PREVIA_RONDA_2.md`.

Scripts nuevos: `hitos_cargar_evidencia_2026.py`, `bajar_entur_gastronomia.py`,
`bajar_idecba_ejes_comerciales.py`.

---

## El titular · el hueco SÍ movía la grilla

La lectura declaraba tres ramas según cuántas filas cambiaran de vía abierta al cargar la
evidencia. **Cambiaron 20 de 94 en la vía B, y 5 cambiaron su número de vías abiertas.**

> Rama declarada: «cambian muchas (>5) → el hueco SÍ movía la grilla, y todo conteo de vía B
> anterior a esta carga queda marcado como **provisorio**».

Los conteos de vía B de la ronda 1 —40 de 94— quedan **superados**. El número vigente es **43 de
94**, y no es sólo tres más: hay filas que abren y filas que cierran.

---

## 1 · TAREA 1 · Las 25 direcciones · **25 de 25 geocodificadas**

Las 20 pizzerías emblemáticas y las 5 heladerías históricas pasan de **cero coordenadas a las 25**.

**San Antonio entró y es el cuarto hito de Boedo.** `via_B_nombres` de Av. Boedo dice ahora
«Café Margot; Esquina Homero Manzi; **San Antonio**». Era el control que la lectura previa había
fijado: si no lo sumaba, el problema era del cruce y no de la evidencia. Lo sumó.

**El Fortín se georreferenció por esquina** —Álvarez Jonte y Lope de Vega—, con la altura **vacía**
y el método anotado en la fila. Y abre vía B en P025-2 Monte Castro, que antes no tenía ninguno.

### Los cinco conflictos: cargados los dos, y medida la consecuencia

No se resolvió ninguno. Se geocodificaron todas las variantes y se midió **la distancia entre
ellas**, que es lo único que puede cambiar un resultado:

| conflicto | variantes | distancia máxima | consecuencia |
|---|---:|---:|---|
| La Mezzetta · GCBA 1311 vs prensa 1321 | 2 | **12 m** | ninguna: misma esquina |
| Banchero · Suárez 396 vs Alte. Brown 1220 | 2 | **28 m** | ninguna: misma esquina, dos numeraciones |
| San Carlos · Rivadavia 4548 vs Rivadavia y La Plata | 2 | **80 m** | ninguna: misma cuadra |
| Saverio · 2809 / 2816 / 2727 | 3 | **136 m** | **material**: pueden caer en polígonos distintos |
| La Americana · Comuna 3 vs Comuna 1 | 1 | — | no es conflicto de dirección: es de atribución |

**Cuatro de los cinco no cambian nada** y eso ahora está medido, no supuesto. El único que puede
cambiar algo es Saverio, y el tramo largo es justamente el local fundacional de San Juan 2727
**que ya no opera**: el conflicto se disuelve solo cuando se aplica la vigencia.

Las variantes viajan enteras en `hitos_variantes_direccion.csv`.

### Casa Burgio · la continuidad no es la vigencia

Se cargó `continuidad_ininterrumpida = no · cerró en 2021 y reabrió en octubre de 2022 con otro
dueño`, separada de `vigencia_verificada = si`. Son dos cosas distintas y el Atlas necesita las dos
por separado: el local abre hoy, y su trayectoria tiene un corte de un año y medio.

---

## 2 · TAREA 2 · Patrimonio normativo · de 2 a **10**

| establecimiento | declaratoria | norma |
|---|---|---|
| Esquina Homero Manzi | Sitio Histórico Nacional | — |
| Peña Los Amigos / Bar El Chino | Sitio de Interés Cultural | norma 421/99 |
| Banchero | Sitio de Interés Cultural | Norma 143/02 |
| Bar Oviedo | Sitio de Interés Cultural + APH 21 (protección Estructural) | — |
| Bar Catedral Tango | Sitio de Interés Cultural | — |
| El Cedrón | Sitio de Interés Cultural | — |
| El Puentecito | Declarado de Interés Cultural | — |
| Antiguo Matadero | Monumento Histórico Nacional + APH 21 | Decreto 1021/1979 ⚠ |
| Mercado de San Telmo | Monumento Histórico Nacional | Decreto 12/2001 |
| **Yiyo el Zeneize** | **patrimonio histórico y cultural inmaterial de su carta gastronómica** | Ley CABA 6.533 |

Siete se marcaron sobre hitos que ya estaban; tres entraron como fila nueva (Peña Los Amigos,
Bar Catedral Tango, Antiguo Matadero).

**Las dos reservas viajan en la columna `patrimonio_nota` de la capa**, no al pie: el Decreto
1021/1979 sale de una fuente barrial y falta confirmarlo contra el registro nacional; el Mercado de
San Telmo se cargó con su dirección real y **sigue 64 m afuera de R03**, que es un problema de la
delimitación de la zona publicada.

Y sobre Yiyo el Zeneize: la Ley 6.533 declara patrimonio **la carta**, no el edificio. Es el único
de los diez donde lo declarado es la práctica gastronómica misma. Si el Atlas quiere un caso que
muestre qué significa «patrimonio gastronómico» en términos normativos, es ése y no tiene
competencia.

> Trampa encontrada: emparejar el patrimonio por nombre plegado fusionó **«Restaurante Oviedo»
> (Recoleta) con «Bar Oviedo» (Mataderos)** —el plegado tira BAR y RESTAURANTE y los dos quedan en
> «OVIEDO»—. Pero exigir la misma calle rompía el Mercado de San Telmo, asentado en Defensa 961 en
> una fuente y en Bolívar 954 en la otra porque **tiene dos frentes**. Lo que desempata es la
> distancia entre los puntos: 150 m tolera dos frentes y no junta dos barrios.

---

## 3 · TAREA 3 · La vigencia, y el caso que la justifica solo

Tres campos nuevos en la capa: `vigencia_verificada`, `vigencia_fuente`, `vigencia_fecha`.

```
no              1     Los Laureles
dudosa          2     Bar Oviedo · Peña Los Amigos / Bar El Chino
si              1     Casa Burgio
sin_verificar 216
```

**`sin_verificar` es un cuarto valor y está puesto a propósito.** Los tres del enunciado suponen
que alguien miró; sobre 220 hitos, alguien miró 4. Rellenar el resto con `si` sería afirmar 216
cosas que nadie comprobó — que es exactamente lo que hace hoy el circuito oficial del GCBA con Los
Laureles.

### La regla nueva y la fila que la prueba

Declarada antes de medir: **un hito verificado como cerrado no abre la vía B**; los dudosos y los
sin verificar sí, y sus conteos viajan al lado.

> **P008 Barracas pasó de abrir vía B a no abrirla.** Su único hito era **Los Laureles**, que cerró
> a fines de julio de 2026. Sin el campo de vigencia, esa fila seguiría certificando trayectoria
> con un bar que ya no existe — y el circuito gastronómico oficial lo seguiría respaldando.

Es una sola fila de 94, y es la razón entera por la que el campo hacía falta.

Los **10 cierres confirmados que no están en la capa** —Bar Lisandro, El Malevo, la sucursal Once
de Banchero, el local fundacional de Saverio y las seis heladerías de Liniers— quedan en
`cierres_registrados_fuera_de_la_capa.csv` como lista de guardia, para que ninguno entre en una
carga futura sin que salte.

### Qué cambió en la capa

| tipo | hitos | con punto (antes) | cerrados | dudosos |
|---|---:|---:|---:|---:|
| Bar Notable | 90 | 90 (84) | 1 | 1 |
| MICHELIN | 58 | 57 (57) | 0 | 0 |
| **Pizzería emblemática** | 20 | **20 (0)** | 0 | 0 |
| Restaurante Icónico | 16 | 16 (16) | 0 | 0 |
| 50 Best | 16 | 16 (16) | 0 | 0 |
| Mercado/patio | 12 | 8 (8) | 0 | 0 |
| **Heladería histórica** | 5 | **5 (0)** | 0 | 0 |
| Patrimonio normativo (filas nuevas) | 3 | 3 (0) | 0 | 1 |

**220 hitos, 215 con punto** (antes 211 y 181). Los 5 que quedan sin ubicar son 4 mercados sin
dirección publicada y 1 MICHELIN. `hitos_capa_unificada.csv` **queda intacto** como estado de
comparación.

---

## 4 · Lo que cambió en las seis vías

| vía | ronda 1 | ronda 2 |
|---|---:|---:|
| A · densidad | 89 de 94 | 89 de 94 |
| **B · trayectoria** | **40 de 94** | **43 de 94** |
| C · mercados | 4 de 94 | 4 de 94 |
| D · comunidades | 7 de 94 | 7 de 94 |
| F · corredor | 53 de 94 | 53 de 94 |

Cinco filas cambiaron su número de vías abiertas: **cuatro suben** —P021 Liniers (El Ciervo),
P066 Barracas (Los Campeones), P044 San Cristóbal (Saverio), P025-2 Monte Castro (El Fortín)— y
**una baja**, P008 Barracas, por el cierre de Los Laureles.

En las 22 publicadas los hitos suben sin cambiar ninguna vía abierta: Palermo 20→21, Centro 18→21,
Corrientes 9→10, Recoleta 9→10, Paternal 1→3, Abasto 2→3, Boedo 2→3, Devoto 2→3. Ninguna de las 22
tiene hitos cerrados adentro. **Las 22 siguen abriendo al menos una vía medible.**

La matriz pasa de **51 a 53 columnas** (`via_B_cerrados` y `via_B_dudosos`); las **23 originales
verificadas contra el commit anterior a la ronda 1: 0 celdas distintas**.

### Una corrección a tu lectura de R13

Dijiste que Abasto entra por **B y D**. Por B sí, con 3 hitos. **Por D no lo puedo medir:** los
cuatro enclaves con límites documentados que me diste no incluyen el **Corredor Peruano de
Agüero**, que es tu argumento para D. La vía D de Abasto necesita ese quinto enclave con su
delimitación textual; sin ella, la columna dice «cerrada» y estaría diciendo «no lo medimos».

---

## 5 · TAREA 4 · El ENTUR · bajado, y **no es lo que esperábamos**

Bajó limpio desde el repositorio: CC-BY-2.5-AR, CSV + GeoJSON + XLSX + SHP.

### La fecha del catálogo no es la fecha de los datos

```
metadata_modified del DATASET   2026-07-22
last_modified de los ARCHIVOS   2019-08-05  y  2019-05-03   ← todos, sin excepción
```

**El dataset es de 2019.** El «actualizado el 22/07/2026» es la fecha del registro del catálogo, no
de los recursos. Citarlo como fuente 2026 sería el mismo error de dieciséis años que estamos
corrigiendo en los ejes comerciales, sólo que de siete.

### Y no puede resolver la vía A «por conteo real»

```
ENTUR (2019)       2.823 puntos en toda la Ciudad
base del barrido  23.981 puntos del anillo núcleo
razón                0,12
```

**Pero la razón no es pareja, y ahí está lo que sí sirve.** Por zona publicada va de **0,02 a
0,25**, y el orden no es casual:

| más cubierto | razón | menos cubierto | razón |
|---|---:|---|---:|
| Centro / Microcentro | 0,25 | Abasto | 0,02 |
| Av. Corrientes | 0,25 | Villa Urquiza | 0,03 |
| San Telmo | 0,25 | Costanera Norte | 0,03 |
| Recoleta | 0,20 | Av. Boedo | 0,04 |
| Puerto Madero | 0,20 | Donado-Holmberg | 0,04 |

Es un catálogo **turístico**, y su cobertura sigue al turismo. Entonces la fuente no sirve para lo
que esperabas —contar— pero **sirve para la otra mitad de tu pregunta**: la razón ENTUR/base es una
medida directa de **sesgo de cobertura turística por zona**, que es el contraste «concentración
medida contra cobertura periodística» expresado en un número. Con el caveat de que la cobertura
es de 2019 y la base de 2026.

**Guardrail 7:** el archivo trae `telefono` y `mail` de cada establecimiento. Son comercios y es
dato abierto, pero la regla nombra emails y teléfonos sin hacer esa distinción y no se la hicimos
nosotros: los crudos quedan **fuera de Git** (`.gitignore`) y se versiona la derivada
`*_sin_contacto`, con el ejemplo tapado también en el perfil de columnas.

---

## 6 · TAREA 5 · Los dos .xlsx del IDECBA · leídos, y las dos delimitaciones estaban mal

### La delimitación vigente de los 48 ejes

**80 tramos para 48 ejes**; 19 ejes tienen más de una calle. En
`idecba/ejes_comerciales_48_vigente.csv` con `eje_id`, `calle`, `altura_desde`, `altura_hasta`.

| eje | usábamos (informe 437, mayo de 2010) | vigente |
|---|---|---|
| Mataderos | Alberdi 5401-6199 | **Av. Alberdi 5501-6299** |
| Liniers | Rivadavia 10801-11699 | **Ramón Falcón 6801-7299** |

**Mataderos se corrió 100 metros** en los dos extremos. El Cedrón (Alberdi 6101) sigue adentro,
así que la conclusión no se mueve — pero la cita sí.

**Liniers cambió de calle.** El eje oficial ya no está sobre Av. Rivadavia: está sobre **Ramón
Falcón**, que es una de las tres calles que vos nombrás para el microcentro boliviano («Falcón,
Ibarrola, Gral. Paz»). El eje comercial oficial y el enclave comunitario coinciden en la calle, y
eso es corroboración independiente de la delimitación de la vía D — no la habíamos buscado.

### El relevamiento del 1.er cuatrimestre de 2026

**12.896 locales relevados · 11.605 ocupados · tasa de ocupación 90,0 %.** Los 48 nombres del
glosario y los del relevamiento **coinciden exactamente**, así que las dos tablas se pueden cruzar
por nombre sin normalizar nada. Están las cuatro medidas por eje —relevados, ocupados, tasa,
densidad comercial por cuadra— y también los tres cuatrimestres anteriores, que permiten serie.

Más densos por cuadra: Avellaneda 23,3 · Libertad 22,8 · Flores Sur 20,2 · Corrientes y Pueyrredón
18,7 · Monte Castro 18,6 · **Liniers 18,2**.

> Trampa: la fila de pie «Fuente: Instituto de Estadística…» cae en la columna `eje` y se colaba
> como un eje 49.º si se filtraba sólo por no nulo. Se corta por la columna que trae medición, y
> ahora la corrida verifica que los 48 nombres de las dos hojas coincidan.

**Lo que esto habilita y no hice** —porque no lo pediste y es una decisión de método—: los 48 ejes
tienen calle y altura, y el callejero permite convertirlos en geometría. Eso daría una medida
oficial e independiente de densidad comercial por corredor, contra la cual contrastar la vía A.

---

## Lo que espera decisión

1. **La vía E**, que seguís llenando vos. Sigue siendo la única columna vacía.
2. **El quinto enclave: el Corredor Peruano de Agüero**, con su delimitación textual, para que
   Abasto pueda abrir vía D medida.
3. **Confirmar el Decreto 1021/1979** contra el registro nacional. Hoy entra marcado, no validado.
4. **La envolvente R03 de San Telmo**, que sigue dejando su mercado 64 m afuera.
5. **Verificar vigencia sobre los 216 `sin_verificar`**, o al menos sobre los hitos que hoy son el
   único de su zona: son los que pueden dar vuelta una fila entera, como pasó con P008.
6. **Convertir los 48 ejes comerciales en geometría** para contrastar la vía A contra una medición
   oficial y actual, si te parece que vale.
7. **Actualizar toda cita de los ejes de Mataderos y Liniers** en documentos ya escritos: la vieja
   delimitación circula en `sur_oeste_seis_vias.csv` y en lo que se haya derivado de ahí.
8. Sigue de antes: las 39 filas que superponen territorio de una vieja, `Ultramarinos` sin
   geocodificar, y el resto del pendiente del handoff del 2026-08-06.
