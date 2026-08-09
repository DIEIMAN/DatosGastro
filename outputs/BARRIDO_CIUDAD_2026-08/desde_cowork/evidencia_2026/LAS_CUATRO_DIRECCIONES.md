# Las cuatro direcciones: el test de Places pasa de dos ramas a cuatro celdas

*8 de agosto de 2026 · la mitad documental de la escalera, hecha antes de gastar un request*

Datos en `places_cuatro_celdas.csv`.

---

## Por qué fui a mirar antes

La escalera de calibración que armé esta mañana da el número de días desde cada cierre. Eso alcanza para medir **cuándo** Places detecta, y no alcanza para saber **qué** detecta.

La hipótesis pre-registrada era binaria: *Places sigue el lugar, o sigue el negocio*. Fui a averiguar qué hay hoy en cada dirección — y aparecieron **cuatro configuraciones distintas**, no dos. Con eso el test deja de ser una escalera y pasa a ser un diseño que discrimina.

Y apareció otra cosa, que va primero porque es un error mío.

---

## Primero: el Palacio de la Papa Frita no es un cierre limpio

Lo puse en la escalera como *«cerrado el 02/03/2026, 159 días, el extremo bajo, cierre masivamente cubierto por prensa»*.

**Es una mudanza con una quiebra encima, y con un cambio de nombre casi imperceptible.**

| fecha | qué pasó |
|---|---|
| noviembre de 2024 | concurso preventivo |
| **3 de marzo de 2026** | **restitución de llaves** del local de Av. Corrientes 1612, esquina Montevideo — Bar Notable desde 2015 |
| 5 de marzo de 2026 | anuncian reapertura *«en nuestra nueva casa en **Paraná 350**, entre Av. Corrientes y Sarmiento»* |
| — | reabre como **«Palacio de las Papas Fritas»** |
| **17 de junio de 2026** | el Juzgado Nacional en lo Comercial N° 7 decreta la **quiebra** de *El Resto de Corrientes S.R.L.*, la firma que lo explotaba |
| — | el juez inhabilita a la gerente y le prohíbe salir del país; ordena verificar si en Paraná 350 continúa la actividad de la fallida y **disponer la clausura inmediata** si se comprueba |

**Motivo del cierre del local histórico: «fuerte incremento en el alquiler» sobre Av. Corrientes.** Eso sí se sostiene.

### Es la misma trampa que The New Brighton, dos veces en un día

Lo cargué como cierre porque los titulares decían *«Cerró El Palacio de la Papa Frita»* y *«El fin de una era»*. **El local histórico cerró; el establecimiento se mudó.** Es FD-20 en su segunda aparición, y esta vez con una vuelta más: el que después quebró fue la sociedad, y eso es un tercer hecho distinto de los dos primeros.

Y trae una variante nueva de la trampa del nombre, que hay que registrar aparte: **«Palacio de la Papa Frita» y «Palacio de las Papas Fritas» difieren en dos letras.** No es un homónimo accidental como las cuatro Perla — es una **variación deliberada**, y un cruce por nombre normalizado casi seguro las une. Si el Atlas las funde, publica como un solo hito vivo lo que un juez está investigando como dos entidades distintas.

> **Regla que sale: en la capa de hitos, la identidad es la dirección más la razón social, nunca el nombre de fantasía.**

### Y corrige dos cosas que ya escribí

**En la capa de memoria** figura como `extinguido`, con causa «alquiler dolarizado que se duplicó a la renovación». **No es `extinguido`: es una mudanza con la dirección histórica perdida.** El estado correcto es el que la capa ya tiene para La Academia.

**En la lámina 11 y en la sección 48 de la edición técnica** está citado como caso de *«los establecimientos de más de noventa años que cerraron»*. Hay que cambiar la frase — **y el cambio mejora el hallazgo**:

> El mecanismo inmobiliario no siempre mata al establecimiento: **a veces lo desplaza.** El Palacio de la Papa Frita se fue de Av. Corrientes 1612 a Paraná 350. La Academia se fue de Callao 368 a Montevideo 341. Lo que se pierde en los dos casos es **la dirección histórica**, que es justamente lo que el catálogo de Bares Notables distingue.
>
> **El patrimonio gastronómico porteño no sólo cierra: se está mudando de sus direcciones históricas por precio del suelo.** Y una designación que está atada a un local pierde su objeto cuando el local se va.

Eso es más verdadero, más incómodo y más útil para una política de patrimonio que «cierran por el alquiler».

---

## Las cuatro celdas

Cada dirección quedó vacante o quedó ocupada de una manera distinta, y **cada configuración predice cosas opuestas según qué siga Places.**

| dirección | qué era | días | **qué hay hoy** |
|---|---|---:|---|
| **Florida 1005** | Plaza Bar | 3.285 | **vacante**, edificio cerrado y en obra, reapertura anunciada para 2028 |
| **Av. Corrientes 1612** | El Palacio de la Papa Frita | **158** | **vacante** — llaves restituidas — y **el negocio se mudó a Paraná 350** |
| **Av. Rivadavia 2800** | La Perla del Once | **3.493** | **otra gastronomía**: la pizzería **La Americana**, operando |
| **Av. L. N. Alem 852** | Mercado de los Carruajes | **465** | **el mismo operador, en uso no gastronómico**: eventos y experiencias, casamientos y corporativos. Concesión de *Mercado de los Carruajes S.A.* vigente hasta febrero de 2027 |

*(Se suma **Av. de Mayo 1152**, Hotel Castelar: **vacante y en venta**, publicado como 9.900 m² y 169 unidades funcionales. Es la réplica de Plaza Bar a unos mil días menos.)*

### Las predicciones, escritas antes de correr

| dirección | si Places sigue **el lugar** | si sigue **el negocio** |
|---|---|---|
| Florida 1005 | `CLOSED` ✔ *ya confirmado* | `CLOSED` ✔ |
| Av. de Mayo 1152 | `CLOSED` | `CLOSED` |
| **Av. Rivadavia 2800** | **`OPERATIONAL`** | **`CLOSED`** |
| **Av. L. N. Alem 852** | **`OPERATIONAL`** | **`CLOSED`** |
| **Av. Corrientes 1612** | **`CLOSED`** | **`OPERATIONAL`** *(perfil migrado a Paraná 350)* |

**Las dos primeras no discriminan** — las dos hipótesis predicen lo mismo. Por eso Plaza Bar solo nunca iba a alcanzar, y conviene decirlo: **el único test que corrimos y acertó era el que no distinguía nada.**

**Las tres últimas discriminan, y Corrientes lo hace en sentido inverso a las otras dos.** No hay resultado intermedio posible: si Places sigue el lugar, sale `OPERATIONAL` en Rivadavia y Alem y `CLOSED` en Corrientes. Si sigue el negocio, exactamente al revés. **Cualquier otro patrón refuta las dos hipótesis** — y eso también es un resultado, porque significaría que el campo no sigue ninguna regla estable y `v2b` no sirve para nada.

### Y el caso de Alem es el más fino de los cuatro

Es el único donde **el negocio sigue existiendo, con el mismo nombre y el mismo operador, en la misma dirección, y dejó de ser gastronómico.** Si Places devuelve `OPERATIONAL` ahí, no está mintiendo: la sociedad opera y el lugar funciona. Está respondiendo otra pregunta.

Eso vuelve explícito algo que conviene tener escrito antes de leer cualquier resultado: **`business_status` no es un campo sobre gastronomía.** Es un campo sobre si una ficha comercial sigue viva. Que lo usemos como proxy de vigencia gastronómica es una decisión nuestra, y sus fallas van a estar donde las dos cosas se separan — que es exactamente lo que pasa en una reconversión.

---

## Lo que falta averiguar, y es una sola cosa

**Qué opera hoy en Suárez 101**, la dirección de La Buena Medida. Es el único cierre real y confirmado del set original, es el que Places falló a 280 días, y **no sé si la dirección quedó vacía o si alguien la ocupó.**

Si quedó vacía y Places dice `OPERATIONAL`, entonces ni la hipótesis del lugar ni la del negocio explican el fallo, y lo que hay es simple latencia. Si está ocupada por otra gastronomía, el fallo queda explicado por la hipótesis del lugar y todo el modelo cierra.

**Es el caso que decide si el fallo de 280 días es un problema de tiempo o de objeto** — y son dos diagnósticos con consecuencias completamente distintas para los 58 hitos del catálogo que nunca fueron mirados.

---

## Una nota chica que puede servir después

El sitio propio del Mercado de los Carruajes no se pudo leer: **el certificado SSL está vencido.**

No lo uso como evidencia de nada, pero vale anotar la idea, porque es barata y es dura: **la fecha de vencimiento de un certificado es un dato fechado y verificable sobre cuándo alguien dejó de mantener un sitio.** No prueba que el local cerró —hay locales abiertos con sitios abandonados— pero es una señal de abandono técnico con fecha, que es más de lo que ofrecen la mitad de las fuentes de este catálogo.

Si en alguna ronda futura hay que ordenar cientos de establecimientos por probabilidad de estar cerrados, ésa es una señal barata de calcular y difícil de falsificar.
