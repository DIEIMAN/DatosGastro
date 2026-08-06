# Cuatro fuentes, una sola receta

**Fecha:** 5 de agosto de 2026 · **actualizado el 5/8/2026 con las corridas de Places**
**Decisión de Diego:** no elegir una fuente, usarlas todas. La documental para el respaldo
oficial, Google Places para lo que las documentales no ven.

> **Qué cambió en esta actualización.** El papel de Places estaba escrito como «la foto de hoy» y
> pasaba a «muestra de vigencia» —no cuántos hay, sino cuáles de los que conocemos siguen
> abiertos—. La medición del 5/8 obliga a corregir esa segunda formulación también, y no por
> matiz: **Places casi no ve los locales que ya conocemos.** Confirma abiertas 26 de las 233
> direcciones núcleo del padrón en Villa Crespo, el 11,2 %. Como sonda de vigencia sobre la base
> conocida es demasiado floja para sostener una tabla.
>
> Lo que sí hace, medido, es traer locales que ninguna fuente documental tiene: en 11 de las 14
> zonas con muestra suficiente, la mayor parte de lo que devuelve son direcciones que el padrón no
> registra. **El aporte de Places es descubrimiento, no vigencia.** El detalle está en el §3 de
> `SPEC_PLACES_BARRIDO.md`.

---

## 1 · El hallazgo que ordena todo esto

**El método ya existe en el repositorio.** Se construyó para el trabajo de casas de pastas, en
junio, y está en `scripts/casas_pastas/`: trece scripts, 3.029 líneas, que hacen exactamente lo
que hace falta acá — consultar Google Places con guardarraíles, clasificar, deduplicar, integrar
con AGC y OSM, auditar cobertura y calidad, y publicar sólo agregados sanitizados.

No hay que diseñar nada. Hay que apuntarlo a otro universo.

Y ese trabajo dejó, además, la evidencia que justifica la decisión. El resultado de integrar
las tres fuentes sobre casas de pastas:

| fuente | candidatos encontrados |
|---|---:|
| OpenStreetMap | 153 |
| Google Places | 152 |
| **Habilitaciones AGC** | **11** |
| **Universo integrado** | **264** |

Sólo 52 de los 264 aparecieron en más de una fuente. **Cada fuente encuentra, en su mayoría,
cosas distintas.** Y la fuente oficial —el padrón de habilitaciones— por sí sola habría
encontrado el 4 % del universo.

Eso es exactamente lo que muestra el factor de captura del Atlas desde el otro lado: las zonas
relevadas en la calle encontraron cinco veces más que el padrón. No es que el padrón esté mal:
es que ninguna fuente sola alcanza.

---

## 2 · Qué aporta cada una

| fuente | qué es | lo que aporta | lo que no |
|---|---|---|---|
| **Habilitaciones AGC** | permisos aprobados 2015-2025 | respaldo oficial, cobertura pareja, trazable | no registra bajas; sólo lo que tramitó |
| **Relevamiento de Usos del Suelo** | censo de uso por parcela, 2017 y 2022-24 | misma densidad en el sur que en el norte; dos cortes para ver variación | clasifica por uso, no siempre separa gastronomía de comercio |
| **OpenStreetMap** | mapeo voluntario, vía Overpass | independiente del Estado y de Google; gratis; contraste puro | cobertura desigual, peor donde más la necesitamos |
| **Google Places** | listado rankeado por relevancia, consultado por celda | **descubrimiento**: locales que ninguna documental tiene. Mediana de 62,5 % de lo que devuelve son direcciones fuera del padrón | no cuenta (recupera ~12 % de un conteo de campo y tiene techo); no confirma vigencia sobre lo conocido (alcanza al 11 % del padrón); términos de uso restringen qué se puede publicar |

La regla de lectura que se desprende: **si una zona coincide en tres o cuatro fuentes, el
número es sólido. Si sólo aparece en una, es una señal, no un dato.** El pipeline de casas de
pastas ya implementa esto como clases de evidencia (A multifuente, A google, A osm, A agc
oficial estricto, B revisión manual).

**Y esa regla ahora está medida sobre gastronomía general, no sólo sobre casas de pastas.** El
cruce de Villa Crespo reparte los 81 puntos de Places en cuatro cajones que son exactamente las
clases de evidencia: 27 coinciden con el padrón, 26 sólo con el Relevamiento, 21 con ninguna
documental y 7 quedan en duda por proximidad. Que el solape entre fuentes sea minoritario dejó de
ser una analogía con el trabajo de junio: es el resultado directo de esta medición.

**El corolario operativo, y es nuevo:** la proporción de lo que Places trae que el padrón ya tiene
—del 7,1 % en La Paternal al 81,8 % en Esmeralda–Paraguay— **mide cuán al día está el padrón en
esa zona**. No hace falta ningún supuesto para leerlo: es un cociente entre dos conjuntos que
están en disco. Es el primer indicador de frescura del padrón que tenemos, y sale de datos ya
pagados.

---

## 3 · Los guardarraíles que ya están escritos

El piloto de Places del repositorio los documenta en su encabezado, y hay que conservarlos tal
cual:

- La API key se lee **sólo** de la variable de entorno `GOOGLE_MAPS_API_KEY`. Nunca se imprime,
  loguea, guarda ni commitea.
- `--dry-run` es el modo por defecto: no hace ninguna llamada real sin `--run`.
- Límites explícitos por corrida: `--max-queries`, `--max-results`, `--pause`.
- Salida a carpeta separada y fuera de Git.
- **Sólo la API oficial. Nada de scraping.**

Y hay un script aparte, `google_places_publicar_sanitizado.py`, que copia a la carpeta
publicable únicamente agregados —por barrio, por comuna, densidades, cobertura— y verifica que
ningún archivo publicado lleve nombre, dirección, razón social ni `place_id`. Eso no es
prolijidad: es lo que permite que un dato de Places alimente un documento público sin
redistribuir contenido de Google.

**Para el Atlas, la consecuencia práctica:** Places puede sostener el *número* de una zona y su
lectura territorial. No puede aparecer como listado de locales con nombre y dirección.

---

## 4 · Lo que cuesta

Verifiqué las franjas gratuitas vigentes de Google Maps Platform: **10.000 llamadas por
producto y mes en Essentials, 5.000 por SKU en Pro, 1.000 por SKU en Enterprise**. Text Search
—que es lo que usa el piloto— cae en Pro, así que son 5.000 llamadas gratuitas por mes.

No pude verificar el precio por cada mil llamadas más allá de la franja: la página de precios
lo remite a una lista aparte que no se pudo leer. **Hay que consultarlo antes de correr un
barrido grande.**

Lo importante para dimensionar: un barrido de 48 barrios con grilla puede irse a varios miles
de llamadas. Conviene estimar el conteo de requests **antes** de ejecutar, y partir el barrido
por mes si hace falta para quedar dentro de la franja gratuita. El piloto ya tiene los
parámetros para eso.

---

## 5 · Lo que yo no puedo hacer desde acá

Mi entorno no tiene salida a la red salvo para leer páginas. Lo comprobé:

- `data.buenosaires.gob.ar` y `cdn.buenosaires.gob.ar` — descarga bloqueada (403)
- `overpass-api.de` — bloqueado
- `places.googleapis.com` — bloqueado

Pude leer la ficha del dataset y la documentación en PDF, y de ahí salieron las URL exactas de
descarga. **Pero los archivos hay que bajarlos desde la máquina del repositorio**, que sí tiene
red. Lo mismo para Overpass y para Places.

Las URL de descarga verificadas del Relevamiento de Usos del Suelo 2022-2024:

| formato | URL |
|---|---|
| CSV | `https://data.buenosaires.gob.ar/dataset/relevamiento-usos-suelo/resource/3c7e5f10-577a-44ea-b614-82cc05f842aa/download` |
| SHP | `https://data.buenosaires.gob.ar/dataset/relevamiento-usos-suelo/resource/613ef164-131b-422a-b9e2-257cee4b46b4/download` |
| XLSX | `https://data.buenosaires.gob.ar/dataset/relevamiento-usos-suelo/resource/dca28a61-18a1-492a-81f1-b0e39d0e48a8/download` |
| Documentación PDF | `https://cdn.buenosaires.gob.ar/datosabiertos/datasets/secretaria-de-desarrollo-urbano/relevamiento-usos-suelo/documentacion-relevamiento-usos-suelo-2022-2024.pdf` |

El corte 2017 también está publicado en GeoJSON, lo que permite comparar 2017 contra 2022-24 y
ver qué se movió:
`https://data.buenosaires.gob.ar/dataset/relevamiento-usos-suelo/resource/6bf6b0b1-53c4-4860-ab78-3f5fb4b398a2/download`

### Lo que dice la documentación del Relevamiento

Leí el PDF. El archivo trae trece campos: `SMP` (nomenclatura catastral),
`Barrio`, `Tipo1` (uso general), `Tipo2` (uso específico), `Estado` (activo/inactivo), `Pisos`,
`GP_Q`, `Obs`, `Calle`, `Puerta`, `Unificado`, `SMP_Idem` y `Año`. **La unidad es la parcela.**

Hay una advertencia importante: la documentación **no publica el diccionario de códigos**. Sólo
menciona que bajo `Unicomercial` existe «restaurante» como valor posible de `Tipo2`. Es decir,
**no se sabe de antemano cuánto separa gastronomía del comercio general: hay que abrir el
archivo y contar los valores distintos de `Tipo2`.** Ese es el primer control, y de su
resultado depende si esta fuente entra como primaria o como auxiliar.

Tampoco dice qué barrios cubre ni si el relevamiento 2022-24 está completo. Segundo control.

---

## 6 · El orden propuesto, y en qué estado está cada paso

1. ~~Bajar el Relevamiento de Usos del Suelo y contar los valores distintos de `Tipo2`.~~
   **HECHO.** Separa gastronomía: entra como fuente primaria. 471 valores de `TIPO2`, mapeados a
   los dos anillos por simetría con el padrón.
2. ~~Bajar el extracto de OSM y contar POI gastronómicos por barrio.~~ **HECHO**, y con él
   entraron dos fuentes más que no estaban en este diseño: **Overture Maps** y **All The
   Places**. Ver el bloque «Ya no son cuatro» al final.
3. ~~Adaptar el piloto de Places al universo gastronómico.~~ **HECHO Y CORRIDO.** 306 requests en
   total; los guardarraíles se conservaron enteros.
4. ~~Estimar el costo del barrido completo antes de ejecutarlo.~~ **HECHO:** 2.100 requests con la
   grilla de 500 m y una familia de consulta. **La grilla está pendiente de redimensionar**, y
   ahora se sabe con qué criterio: estaba calculada para contar, y contar no es lo que Places
   hace. El CSV no se tocó; el criterio nuevo está en `AVISO_GRILLA_48_BARRIOS.md`.
5. ~~Integrar las cuatro fuentes con las clases de evidencia del pipeline existente.~~ **HECHO, y
   mejor que eso:** las clases de evidencia se reemplazaron por el esquema de dos tablas
   (`ESQUEMA_BASE_GASTRONOMICA.md`), donde la procedencia se guarda por fuente en vez de
   resolverse a una clase. Ver `README_BASE_GASTRONOMICA.md`.
6. ~~Recalcular el factor de captura de las 22 zonas contra el universo integrado.~~ **HECHO**
   —`cotejar_22_zonas_base.py`—, con la advertencia de que la base todavía no tiene Places.

---

## 7 · Ya no son cuatro

Este documento se escribió con cuatro fuentes en la cabeza. Al bajar OSM aparecieron dos más que
lo cambian todo, y la tabla del §2 queda corta. El cuadro completo, con lo medido el 5/8:

| fuente | núcleo en la Ciudad | ÷ padrón | licencia |
|---|---:|---:|---|
| **Overture Maps** | **11.921** | **1,74** | CDLA-Permissive-2.0 |
| Relevamiento de Usos del Suelo | 9.108 parcelas | 1,33 | CC-BY-2.5-AR |
| Habilitaciones AGC (F02) | 6.861 direcciones | 1,00 | CC-BY-2.5-AR |
| OpenStreetMap | 6.427 | 0,94 | ODbL (compartir-igual) |
| All The Places | 282 | 0,04 | CC0 1.0 |
| Google Places | ~12 % de un conteo de campo | — | no redistribuible |

**Y la conclusión de este documento se da vuelta.** Decía que ninguna fuente sola alcanza y que
Places aportaba descubrimiento propio. Lo primero sigue siendo cierto. Lo segundo hay que
corregirlo con el número: de los 81 puntos que Places trajo de Villa Crespo, **Overture sola
empareja 73** y la unión de las abiertas empareja 74. **Places descubre casi lo mismo que Overture
ya tiene, y con la desventaja de no poder publicarse.**

**Decisión abierta para Diego:** correr o no una primera tanda de Places, y de qué tamaño. La
recomendación cambió y está en `HANDOFF_BASE_GASTRONOMICA_2026_08_05.md`.
