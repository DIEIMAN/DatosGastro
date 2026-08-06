# La base gastronómica de la Ciudad

**Qué es:** una fila por local, con la procedencia de cada fuente guardada aparte y sin resolver.
**Para qué existe:** para que los polos gastronómicos de toda la Ciudad se puedan dibujar y
defender. La base es el medio; el mapa de polos poligonizados sigue siendo el entregable.

Esquema completo: [`ESQUEMA_BASE_GASTRONOMICA.md`](ESQUEMA_BASE_GASTRONOMICA.md).
Generador: `scripts/barrido_ciudad/build_base_gastronomica.py`.

---

## ⚠ Licencias · leer antes de publicar cualquier capa

**Esta lectura es de trabajo, no un dictamen. Antes de publicar, que la revise el área legal de la
Dirección.** No es una fórmula de cortesía: hay una condición concreta que puede cambiar qué se
puede publicar y bajo qué términos.

| fuente | licencia | qué exige al redistribuir |
|---|---|---|
| F01 · oferta gastronómica (Ente de Turismo) | CC-BY-2.5-AR | atribución |
| F02 · habilitaciones (AGC) | CC-BY-2.5-AR | atribución |
| Relevamiento de Usos del Suelo | CC-BY-2.5-AR | atribución |
| Permisos de uso del espacio público | CC-BY-2.5-AR | atribución |
| **OpenStreetMap** | **ODbL** | **atribución + compartir-igual sobre bases derivadas** |
| Overture Maps | CDLA-Permissive-2.0 | atribución |
| All The Places | CC0 1.0 | nada |
| Wikidata | CC0 1.0 | nada. **Pero su coordenada no se importa: ver abajo** |
| Registro Nacional de Sociedades | CC BY 4.0 | atribución. **El CUIT no se exporta nunca** |
| IGJ · Entidades constituidas | CC BY 4.0 | atribución |
| **Google Places** | **términos de uso de Google** | **no se redistribuye nombre, dirección ni `place_id`** |

**El punto que hay que resolver, y es de fondo:** la ODbL de OpenStreetMap tiene cláusula de
compartir-igual **sobre la base derivada**, no sólo sobre los registros que vienen de OSM. Una base
pública que incorpore atributos o geometrías de OSM puede quedar alcanzada por esa cláusula
completa, incluidas las partes que vinieron de fuentes permisivas. Mezclar ODbL con licencias
permisivas en un mismo producto derivado tiene condiciones propias y **no las decide el equipo
técnico**.

Hay una salida técnica si el área legal considera que la cláusula complica la publicación, y
conviene saber que existe antes de la reunión: **la base funciona sin OSM.** Overture aporta 11.921
puntos núcleo contra los 6.427 de OSM, es CDLA-Permissive y no arrastra compartir-igual. OSM entra
como cuarta fuente independiente y como corroboración, no como columna vertebral. Si hubiera que
publicar una capa sin ODbL, se puede construir excluyendo los registros cuyo único origen sea OSM,
y el generador ya guarda la procedencia registro por registro para poder hacerlo sin rehacer nada.

### Plataformas de delivery y reseñas: excluidas por contrato · decisión tomada el 2026-08-05

**PedidosYa, Rappi, Uber Eats y TripAdvisor no entran a esta base, y el motivo no es técnico.**
Se anota acá con las citas para que la línea no se reabra: no hay endpoint que encontrar ni
convenio que gestionar, los términos de uso no permiten el uso.

| plataforma | cláusula | qué dice |
|---|---|---|
| **Rappi** | 5.1.G | prohíbe «acceder, utilizar y/o manipular los datos de RAPPI, Comercios Aliados…» |
| **Rappi** | 10.2 | limita el uso a «personal, privado y no lucrativo» |
| **PedidosYa** | términos de uso | prohíbe «modificar, copiar, reutilizar, extraer, explotar…» |
| **TripAdvisor** | Content API | «Caching, storing or indexing is not permitted for any content except Location ID attribute», tope de 125 caracteres |
| **Uber Eats** | — | no tiene API pública de comercios |

Es el complemento del guardarraíl 6, que prohíbe el scraping de estas plataformas: **aun con
acceso autorizado, los términos no permiten el uso que esta base necesita.**

### La coordenada de Wikidata no se importa

Wikidata es CC0 y su licencia no pone ninguna condición. Aun así **su coordenada no entra**: el
wiki de OpenStreetMap advierte que muchas vienen de Wikipedia, que a su vez las tomó de Google
Maps. Procedencia viciada. De Wikidata se toman atributos —nombre canónico, año de fundación,
declaratoria patrimonial— y la posición se resuelve geocodificando con USIG desde la dirección
postal, que el 97 % de los ítems trae.

**La procedencia de un dato importa aunque la licencia declarada sea permisiva.** Es el mismo
criterio por el que se descartó Wikimapia, que es CC BY-SA.

---

## Las dos tablas

### `local` — la entidad resuelta

Una fila por local. Es lo que consume el clustering.

| campo | qué es |
|---|---|
| `local_id` | identificador propio y correlativo (`LOC000001`). Nunca derivado de un id externo |
| `lon`, `lat` | punto de consenso, por **prioridad de precisión** y no por promedio |
| `smp` | clave catastral, cuando alguna fuente la aporta |
| `direccion_norm`, `nombre` | la mejor disponible entre las fuentes |
| `barrio`, `comuna` | **por geometría**, nunca por el campo de texto de la fuente |
| `barrio_por_cercania` | `True` si el punto cayó en la banda de borde y el barrio es el más cercano |
| `anillo` | `nucleo` / `ampliado` / `fuera` |
| `n_fuentes` | **grupos de independencia**, no fuentes. Ver abajo |
| `fuentes`, `grupos_independencia` | cuáles, en claro |
| `apto_geometria` | si este punto puede participar del dibujo |
| `precision_punto`, `dispersion_m` | de qué fuente salió el punto y cuánto discrepan las demás |
| `nivel_publicacion` | `abierto` / `punto` / `agregado` |
| `frescura` | fecha de la evidencia positiva más reciente. **Nunca «abierto»** |
| `revisado` | `auto` / `pendiente` |
| `corte` | fecha de construcción de esta versión |

### `local_fuente` — lo que dice cada fuente

Una fila por (local, fuente, registro). Muchas por local. Guarda el punto, el nombre, la dirección
y la categoría **tal como los da cada fuente**, sin corregir, más `criterio_match`, `score_match` y
`revisado`.

**La regla dura: no se colapsan las fuentes a un registro «verdadero».** Si mañana alguien discute
un local, la respuesta está acá. Si sólo existiera `local`, la respuesta sería una decisión que ya
nadie puede reconstruir.

---

## Cuatro decisiones que conviene entender antes de usar la base

### 1 · `n_fuentes` cuenta grupos, no fuentes

Overture incorpora a Foursquare y a All The Places como aportantes: las tres son **un solo grupo**.
F01 y F02 son dos trámites distintos del mismo Gobierno pero universos distintos, y cuentan como
dos. Sin esto, `n_fuentes` infla y la corroboración deja de significar nada.

Medido sobre el recorte de la Ciudad, además, **OSM no aporta un solo registro a Overture**: las
dos sí son independientes acá, y su solape mide algo.

### 2 · La proximidad sola no fusiona

Tres criterios pueden pegar dos registros: `smp` (misma parcela), `usig_exacta` (misma calle y
altura dentro de ±10) y `proximidad_y_nombre`. **La proximidad sin nombre ni dirección no fusiona
nunca**, y los pares que sólo la tienen quedan en `pares_pendientes_de_revision.csv`.

No es prudencia decorativa: la fusión es transitiva. Sobre una avenida, una cadena de vecinos a
menos de cuarenta metros uno del otro terminaría siendo un solo local de doscientos registros. El
error no se vería en el total —los locales bajan— y arruinaría el mapa, que es justo lo que la base
tiene que proteger.

### 3 · `apto_geometria` protege el mapa

No es apto un punto sin coordenada, ni uno cuyas fuentes lo ubican a más del umbral declarado unas
de otras. **Una envolvente no puede dibujarse mayoritariamente con puntos no aptos**: es
exactamente el defecto que ya tuvo el Atlas, donde ocho referencias sin puntos terminaron con
envolventes derivadas de la geometría de consulta y no de la oferta. Se previene con un campo, no
con cuidado.

### 4 · `frescura` no dice «abierto»

Es la fecha de la **evidencia positiva más reciente** que alguna fuente ofrece. Un local con
frescura 2024 puede haber cerrado en 2025 y ninguna de estas fuentes se habría enterado. Las fechas
futuras se descartan: un permiso que vence en 2031 no es evidencia de 2031, es evidencia del día en
que se otorgó.

---

## Qué NO hace esta base

- **No es un censo.** Un local sin trámite, sin ficha en ninguna plataforma y sin presencia en
  ningún padrón no aparece. Los carros de choripán de la Costanera son parte de la gastronomía de
  esa zona y no van a estar. Es un límite del trabajo, no una afirmación sobre esos locales.
- **No dice qué está abierto hoy.** Dice cuándo fue la última señal de actividad.
- **No mide facturación, empleo ni superficie.**
- **No reemplaza a ningún registro oficial.**
- **No corrige las cifras publicadas del Atlas.** El cotejo de las 22 zonas
  (`generado/COTEJO_22_ZONAS_BASE.txt`) explica las diferencias por familia de método; no las
  resuelve a favor de ninguna de las dos.

---

## Google Places no está cargado

Por decisión del 5 de agosto: primero se carga todo lo abierto y **recién después** se dimensiona
qué agrega Places. La estructura está lista para recibirlo —tiene su grupo de independencia
(`GOOGLE`) y su regla de publicación (`agregado`)— y el cargador no existe a propósito.

El número que sostiene esa decisión está medido, no supuesto: de los 81 puntos que Places trajo de
Villa Crespo, **Overture sola empareja 73 (90,1 %)** y la unión de las tres fuentes abiertas
empareja 74 (91,4 %). **Sólo 4 de 81 quedarían en `agregado`**, es decir sin identidad publicable.

---

## Cómo se regenera

```powershell
.venv\Scripts\python.exe -W ignore scripts\barrido_ciudad\build_base_gastronomica.py
.venv\Scripts\python.exe -W ignore scripts\barrido_ciudad\cotejar_22_zonas_base.py
```

Antes hay que tener bajadas las fuentes, cada una con su propio script y todas sin costo:

```powershell
.venv\Scripts\python.exe -W ignore scripts\barrido_ciudad\bajar_osm_gastro.py --run
.venv\Scripts\python.exe -W ignore scripts\barrido_ciudad\bajar_overture_places.py --run
.venv\Scripts\python.exe -W ignore scripts\barrido_ciudad\bajar_all_the_places.py
.venv\Scripts\python.exe -W ignore scripts\barrido_ciudad\bajar_fuentes_gcba.py
```

`local.csv` y `local_fuente.csv` **no se versionan**: pesan y se regeneran. Lo que se versiona es
el generador, el informe (`generado/BASE_GASTRONOMICA.txt`) y los agregados por barrio.

## Dependencia nueva

El recorte de Overture usa **DuckDB** sobre el GeoParquet público en S3, para no bajar los 75
millones de POI del mundo. Se instala con `.venv\Scripts\python.exe -m pip install duckdb` y sólo
lo necesita `bajar_overture_places.py`; el resto de la cadena corre sin él.
