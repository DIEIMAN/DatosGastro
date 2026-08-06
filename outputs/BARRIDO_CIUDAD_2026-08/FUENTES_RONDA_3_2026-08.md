# Tercera ronda de fuentes · qué entra, qué no, y qué queda cerrado

**5 de agosto de 2026** · Cierra la búsqueda de fuentes nuevas para la base gastronómica.
Continúa `FUENTES_NUEVAS_2026-08.md`, que sigue vigente en todo lo que no se contradiga acá.

Las rondas anteriores dejaron la base en siete fuentes y 27.727 locales. Esta ronda contesta una
pregunta más chica y más útil: **qué queda afuera y por qué**, para que nadie vuelva a abrir las
mismas líneas dentro de seis meses.

---

## 1 · Lo que entra

### Registro Nacional de Sociedades — el mejor hallazgo de la ronda

<https://datos.jus.gob.ar/dataset/registro-nacional-de-sociedades>
Metadata: <https://github.com/datos-justicia-argentina/Registro-Nacional-de-Sociedades/blob/master/Registro-Nacional-de-Sociedades-metadata.md>

| | |
|---|---|
| organismo | Subsecretaría de Asuntos Registrales, Ministerio de Justicia |
| licencia | **CC BY 4.0 — redistribuible con atribución** |
| formato | ZIP anuales 2019–2026, más el primer semestre de 2026 |
| corte | datos al 31/07/2026, actualización mensual |
| georreferencia | **no trae coordenadas.** Domicilio estructurado: provincia, localidad, calle, número, piso, departamento, CP |
| identificador | CUIT |
| rubro | `actividad_codigo`, **sólo desde diciembre de 2024** |

**Cómo entra: como capa de cruce por CUIT contra el padrón de habilitaciones, NO como universo.**
La distinción no es formal. Dos límites la fuerzan, y los dos hay que declararlos en la base:

- **domicilio legal ≠ local comercial.** Una sociedad puede tener domicilio legal en el estudio
  de su contador y el restaurante a treinta cuadras. Contar sociedades como locales produciría un
  polo gastronómico en la zona de estudios jurídicos del Centro;
- **no incluye monotributo.** Una parte grande de la gastronomía de la Ciudad no está constituida
  como sociedad. Un universo armado sobre esta fuente estaría sesgado hacia lo formal y lo grande,
  que es exactamente el sesgo contra el que trabaja este proyecto.

Lo que sí aporta, y ninguna otra fuente tiene: **razón social y antigüedad registral** para los
locales que ya están en la base, y `actividad_codigo` de la rama 56 como control de rubro sobre el
padrón. Se filtra CABA + rama 56 y se cruza por CUIT.

**Privacidad — la condición de entrada.** El CUIT es dato sensible bajo el guardarraíl 7. Se usa
**sólo como clave de cruce en memoria** y no se escribe en ninguna salida, ni siquiera interna: la
columna se descarta antes de que nada toque el disco, con el mismo mecanismo de `usecols` por
lista permitida que ya usan las seis fuentes del GCBA. Sin geocodificar con USIG desde el
domicilio, esta fuente no aporta un punto; con USIG geocodificado, aporta atributos, nunca
posición nueva.

### IGJ · Entidades constituidas

<https://datos.jus.gob.ar/dataset/entidades-constituidas-en-la-inspeccion-general-de-justicia-igj>

CC BY 4.0, jurisdicción CABA, corte al 30/04/2026, actualización mensual. Publica cinco tablas
—entidades, **domicilios**, balances, autoridades y asambleas— en ZIP por semestre desde 2016.

La tabla de domicilios aparte es lo que la hace usable: permite el cruce sin abrir las tablas de
autoridades ni de balances, que traen nombres de personas físicas y cifras. **Esas dos tablas no
se bajan.** No es una precaución genérica: bajarlas para «ver qué hay» ya sería tratamiento de
datos personales sin necesidad.

Mismo tratamiento que el Registro Nacional: capa de cruce, no universo.

### Wikidata — medido, y el resultado sorprende

CC0 puro. El entorno de la ronda anterior bloqueaba los endpoints SPARQL; acá corrió.
Script: `scripts/barrido_ciudad/bajar_wikidata_gastro.py` · informe:
`generado/WIKIDATA_GASTRO_CIUDAD.txt`.

| | |
|---|---|
| ítems georreferenciados en la caja de la Ciudad | 6.568 |
| de ésos, gastronómicos **por tipo** | **33** |
| gastronómicos **por declaratoria** («Bar Notable») | **95** |

**La advertencia de volumen bajo era correcta, y el motivo por el que era correcta no.** No es que
Wikidata tenga poca gastronomía porteña: es que **81 de los 95 Bares Notables están cargados como
«edificio»**, no como bar ni café. Al catalogarlos, lo enciclopédico fue el inmueble. Filtrar por
tipo (`P31`) encuentra 33; preguntar por la declaratoria encuentra 95.

Es una trampa general de la fuente y conviene anotarla: **`P31` describe qué es la entidad, no qué
actividad pasa adentro.**

Y hay un hallazgo institucional incómodo: **el barrido del catálogo de BA Data —453 datasets— no
devolvió ningún dataset con la lista de Bares Notables.** Hoy el índice abierto más completo de
los Bares Notables de la Ciudad está en Wikidata, bajo CC0, y no en el portal del Gobierno que los
declaró. Dicho con el cuidado que corresponde: puede existir y no estar catalogado con esa
palabra; lo verificable es que el barrido no lo encontró.

**El 97 % trae dirección postal**, que es la salida limpia al problema de la coordenada: se
geocodifica con USIG y la coordenada de Wikidata no se toca. Dos cuidados que se respetaron:

1. **No entra como universo ni como grupo de independencia propio.** Un local que sólo existe en
   Wikidata no crea un registro: su existencia la afirma un editor voluntario. La excepción
   parcial es la declaratoria, que es un acto administrativo de la Ciudad y no una opinión — pero
   el que la transcribió sí es un voluntario, así que la lista se confirma contra la normativa
   antes de darla por buena.
2. **Su coordenada no se copia.** El wiki de OSM advierte que muchas coordenadas de Wikidata
   vienen de Wikipedia, que las tomó de Google Maps: procedencia viciada. Acá se usó sólo para
   acotar la consulta —el servicio de caja es la única forma de que el endpoint no expire— y viaja
   rotulada `coordenada_no_usable`.

---

## 2 · Negativos limpios · no volver a buscar acá

Cada uno con el motivo, para que el descarte sea reutilizable y no haya que rehacer la búsqueda.

| fuente | veredicto | por qué |
|---|---|---|
| **GeoNames** | **cero aporte gastronómico** | revisado el listado completo de *feature codes*: **no existe código para restaurante, bar ni café**. Sirve como toponimia y nada más |
| **Pelias / Geocode Earth** | descartada como fuente | son límites administrativos y direcciones, no locales |
| **Who's On First** | descartada como fuente, **útil como capa base** | mismo motivo; pero tiene polígonos de barrios de CABA con licencia compatible, y sirven para recortar polos |
| **Geoapify** | aporte incremental nulo | es OSM reempaquetado bajo ODbL. Si ya está OSM, no agrega nada y sí agrega una obligación de licencia |
| **datos.gob.ar** | nada nacional | la búsqueda «gastronómico» devuelve **cero datasets** |
| **Datos de Turismo (Yvera)** | nada usable | 15 datasets, ninguno de establecimientos gastronómicos |
| **Michelin** | irrelevante para polígonos | 56 establecimientos en Buenos Aires. Sirve como capa de atractor y se carga a mano |
| **FEHGRA / AHRCC** | descartadas (ronda 1) | no publican listado de asociados por barrio ni direcciones |

---

## 3 · Dos advertencias operativas

### Nominatim público: no usarlo para geocodificar en volumen

La política de uso de la OSM Foundation lo prohíbe expresamente: **«bulk geocoding is not
encouraged»**, límite de **1 request por segundo**, y prohibición explícita de descargar listas de
POI de un área. No es una recomendación de cortesía sobre infraestructura donada: es la condición
bajo la cual el servicio se ofrece, y saltearla expone a un bloqueo por IP que además afectaría a
cualquier otra área del Gobierno que la use.

**Si hace falta geocodificar el padrón, hay dos caminos: montar una instancia propia, o usar USIG
—que ya está integrado, es del propio Gobierno de la Ciudad y no tiene este límite.** La segunda
es la que corresponde por defecto.

### Wikimapia: descartada pese a ser CC BY-SA

Dos motivos, y el segundo es el que decide:

1. límites de API muy restrictivos;
2. el wiki de OSM señala que sus datos se trazaron sobre imágenes de Google Maps, lo que los
   volvería **obra derivada sin licencia**.

Para una base pública de gobierno, ese riesgo no vale lo que la fuente aporta. Es el mismo
criterio que se aplicó a las coordenadas de Wikidata, y conviene que sea el mismo: **la
procedencia de un dato importa aunque la licencia declarada sea permisiva.**

---

## 4 · Plataformas de delivery · excluidas por contrato, no por técnica

PedidosYa, Rappi, Uber Eats y TripAdvisor quedan afuera. **El motivo no es técnico.** Conviene que
quede en el expediente con las citas, porque es la línea que más se reabre.

| plataforma | cláusula | qué dice |
|---|---|---|
| **Rappi** | 5.1.G | prohíbe «acceder, utilizar y/o manipular los datos de RAPPI, Comercios Aliados…» |
| **Rappi** | 10.2 | limita el uso a «personal, privado y no lucrativo» |
| **PedidosYa** | términos de uso | prohíbe «modificar, copiar, reutilizar, extraer, explotar…» |
| **TripAdvisor** | Content API | «Caching, storing or indexing is not permitted for any content except Location ID attribute», con tope de 125 caracteres |
| **Uber Eats** | — | **no tiene API pública de comercios** |

**Ninguna ofrece una vía licenciada** para lo que este proyecto necesita. No hay plan alternativo
que explorar: la decisión no depende de encontrar el endpoint correcto.

Y es coherente con el guardarraíl 6, que ya prohíbe el scraping de estas plataformas. Lo que se
agrega acá es el otro lado: **aun con acceso autorizado, los términos no permiten el uso.**

---

## 5 · Lo que Diego está gestionando puertas adentro

Cuatro fuentes que no dependen de este repositorio y que valen más que todo lo que quedó afuera en
esta ronda:

1. **Certificados de Aptitud Ambiental — APRA**
2. **Padrón de Ingresos Brutos con domicilio — AGIP**
3. **Tabulado especial del Censo Económico por comuna, rama 56 — INDEC**
4. **Diccionario de códigos del Relevamiento de Usos del Suelo**

Los enganches quedan preparados en el esquema: ver
[`ESQUEMA_BASE_GASTRONOMICA.md` §11](ESQUEMA_BASE_GASTRONOMICA.md). Las tres primeras entran como
fuentes en `local_fuente` con su grupo de independencia definido. **El tabulado del INDEC no entra
como filas**: entra como **denominador de completitud por comuna**, que es lo que va a permitir
decir si la cobertura de la base es pareja o si un polo aparece sólo donde consultamos más. Es la
pieza que hoy falta para poder afirmar cualquier cosa sobre cobertura.

---

## 6 · Pendientes menores

- **Foursquare**: Diego abre la cuenta. Baja prioridad, y está medido por qué: aporta el 3,3 % de
  Overture y ya viaja adentro de Overture.
- **Los PDF no se regeneran** hasta el visto de Patricia sobre el cambio de nombre de fuente.
