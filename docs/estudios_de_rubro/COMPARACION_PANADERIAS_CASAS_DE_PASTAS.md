# Panaderías y casas de pastas, lado a lado

2026-08-27, tarde. Los dos estudios corren hoy con el mismo lector compartido, el mismo
esquema de universos A/B/C y la misma caché de geocodificación, así que por primera vez son
comparables.

**Advertencia sobre las cifras de pastas:** las que van acá salen de correr el build
corregido a una carpeta de prueba, y son las del **padrón oficial** (F01 + F02).
`outputs/casas_pastas/` sigue publicando 10, que es lo que veía el lector roto.
Regenerarlo es decisión pendiente de Diego (punto 2 de `ACCIONES_PARA_DIEGO.md`).

**No confundir con el entregable.** El informe y el PDF de casas de pastas publican **254**
establecimientos, que es un padrón candidato integrado: OSM, Google Places, revisión manual
y AGC. El aporte del padrón oficial a ese 254 es la fila `solo AGC = 11`, y **ésa** es la
que el lector roto subestimó. Ver la sección "Qué le hace el lector al entregable de pastas".

## El cuadro

| | Panaderías | Casas de pastas |
|---|---|---|
| Universo A (núcleo) | 1.219 | 159 |
| Universo B (frontera) | 513 | 2 |
| A + B | 1.732 | 161 |
| Geolocalizados (A) | 1.203 — 98,7 % | 153 — 96,2 % |
| Con nombre de establecimiento | 117 — 6,8 % | 18 — 11,2 % |
| Marcados para revisión manual | 559 — 32,3 % | 27 — 16,8 % |
| Barrios con al menos uno | 48 de 48 | 42 de 48 |
| Grupo de dedup más grande | 362 registros | 40 registros |
| Cifra publicada hoy en `outputs/` (padrón oficial) | 1.219 | **10** |
| Cifra del entregable (informe y PDF) | — sin informe | **254** (integrado multifuente) |

**Las dos columnas no están en el mismo momento.** Panaderías cuenta por habilitación
desde el 2026-08-28 (fase F1); la columna de pastas todavía sale de agrupar por partida
matriz, que es el inmueble. Cuando se regenere pastas con la clave nueva, su 159 se va a
mover, casi seguro hacia arriba.

## Qué se aprende de compararlos

### 1. Panaderías es 7,4 veces más grande, y eso cambia qué problemas tiene

Con 159 establecimientos, casas de pastas se puede revisar entero a mano. Con 1.732, no:
por eso panaderías necesitó el diagnóstico y las fases F1 y F2 del plan, y pastas puede
saltar directo a la revisión humana.

La regla que sale de acá: **por debajo de ~200 establecimientos conviene revisar todo; por
encima, hay que invertir primero en medir la calidad del padrón.**

### 2. La frontera de panaderías es enorme y la de pastas no existe

En pastas el universo B tiene **2 casos**. En panaderías tiene **471**, un 29 % del total.

No es una asimetría de método: es del rubro. "Casa de pastas" es una categoría nítida —se
elabora pasta o no—, mientras que entre la panadería y la confitería hay un continuo, y la
AGC lo refleja con un rubro entero para el punto de cocción que recibe la masa ya
elaborada. La decisión de alcance en panaderías mueve la cifra un 40 %; en pastas es
irrelevante.

**Consecuencia para el próximo rubro:** antes de empezar, mirar cuántas filas caen en la
zona gris. Si son muchas, la definición hay que discutirla con Diego antes de escribir el
clasificador, no después.

### 3. Panaderías está mejor geolocalizada, y no por mérito propio

99,1 % contra 96,2 %. La diferencia es que la corrida de USIG se hizo apuntando a las
direcciones de panaderías; pastas se benefició de rebote, por compartir la caché. Correrla
apuntando a pastas cerraría también esos 25 casos.

Es un argumento a favor de la caché compartida: el trabajo hecho para un rubro le sirve al
siguiente sin volver a consultar el servicio.

### 4. El defecto de conteo de panaderías probablemente también esté en pastas

El grupo de dedup más grande de pastas fusiona 40 registros; el de panaderías, 360. Los dos
agrupan por partida matriz, que identifica el inmueble y no el local. En panaderías eso
resultó ser un sub-conteo del 9,2 %.

**Nadie lo midió todavía en pastas.** El arreglo de F1 vive en el módulo compartido y en la
clave de agrupamiento, así que si se hace bien, pastas lo hereda. Conviene medirlo ahí
antes de regenerar el entregable, para no rehacer el informe dos veces.

### 5. Ninguno de los dos tiene nombres, y es el mismo motivo

7,2 % y 11,2 %. En los dos casos el campo con el nombre es `titulares`, que no se lee por
guardrail 7. **Es un problema compartido, no de un rubro**, y por lo tanto conviene
resolverlo una sola vez: una pasada de OSM/Overture sobre todas las direcciones del
proyecto, no una por estudio.

### 6. Los universos se pisan

29 domicilios —y las mismas 29 partidas— están en los dos padrones: el 18 % de las casas de
pastas comparte dirección con una panadería. Son habilitaciones que declaran los dos
rubros.

No es un error, pero **sumar estudios de rubro para estimar un total contaría esos locales
dos veces**. Cuando haya tres o cuatro rubros hechos, va a hacer falta una vista que los
concilie.

Detalle en `outputs/panaderias/analisis/d7_solape_con_casas_de_pastas.csv`.

### 7. La composición interna es opuesta

Pastas: 158 de 159 son `elaboracion_pastas_frescas`. Un solo patrón explica el universo.

Panaderías: 625 elaboración con venta directa, 453 despacho, 55 n.c.p., 39 industrial, 4
panificadora. Cinco patrones que describen negocios distintos —hornear, revender, producir
para terceros— metidos en una sola cifra.

Por eso panaderías necesita una decisión editorial sobre qué se publica y pastas no.

## Qué le hace el lector al entregable de pastas

Medido el 2026-08-28, después de que la comparación anterior se leyera mal.

El informe entregado (`INFORME_CASAS_PASTAS_INTEGRADO_V4`, y el PDF DGDGAS que sale de él)
publica **254 candidatos únicos**, desglosados por fuente en su propia sección 2:

| Combinación | Candidatos |
|---|---|
| solo OSM | 92 |
| solo Google | 90 |
| Google + OSM | 53 |
| **solo AGC / F02** | **11** |
| recall complementario | 7 |
| documental | 1 |
| **total** | **254** |

Ese **11** (10 del universo A + 1 de B) es lo que produjo el lector roto. Con el lector
arreglado el padrón oficial da **159** en el universo A. El informe, entonces, afirma en su
tabla de fuentes que el registro administrativo ve 11 casas de pastas en la Ciudad, y ve
unas 159: **un factor de 14**.

### Cuánto movería el total

Cruce por proximidad de las 153 filas geolocalizadas del universo A corregido contra las
259 filas con coordenadas del padrón integrado interno (`padron_candidato_integrado_v2`):

| Umbral | Ya en el integrado | Sin correspondencia |
|---|---|---|
| 25 m | 56 | 97 |
| 50 m | 56 | 97 |
| 75 m | 59 | 94 |

La estabilidad entre 25 y 75 m indica correspondencia real y no un artefacto de distancia.

**Orden de magnitud: el integrado pasaría de 254 a ~350.** Es una cota superior y no una
cifra publicable: el cruce es por proximidad sin comparar nombre, y las ~97 sin
correspondencia no fueron revisadas a mano —parte serán habilitaciones de locales cerrados,
que es exactamente lo que F02 no puede distinguir (guardrail 5).

### Advertencia sobre el mapa sanitizado

El geojson del pack público (`mapa_puntos_sanitizado_v3_depurado.geojson`) trae las
coordenadas redondeadas a tres decimales, o sea una grilla de ~100 m. **No sirve para
cruces finos**: un match a 30 m contra ese archivo mide el redondeo, no la coincidencia.
Para cruzar hay que usar el padrón interno, que conserva la precisión.

## Lo que conviene hacer con esto

1. **Medir en pastas el efecto de la unidad de conteo** antes de regenerar su entregable.
   Es la misma corrida de prueba que F1, apuntada al otro rubro.
2. **Resolver los nombres una vez para los dos**, con fuentes abiertas.
3. **Cuando se regenere pastas, hacerlo con F1 ya aplicado**, para no rehacer el informe y
   el PDF dos veces.
4. **Anotar en la receta de rubro nuevo** el paso de medir la zona gris antes de escribir
   el clasificador (punto 2 de arriba).
