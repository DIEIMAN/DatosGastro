# Fuentes nuevas para el barrido de la Ciudad completa

**Fecha:** 5 de agosto de 2026 · **Método:** búsqueda web con verificación de URL una por una.
Se excluyeron las dieciséis fuentes ya catalogadas en `dim_fuente` (F01 a F16).

---

## Las dos que cambian el tablero

### Relevamiento de Usos del Suelo — DG Estadística y Censos + Subsecretaría de Planeamiento

<https://data.buenosaires.gob.ar/dataset/relevamiento-usos-suelo> · CSV, XLSX, SHP y GeoJSON

**Georreferencia: sí, parcela por parcela.** Toda la Ciudad. Cuatro relevamientos: 2008-10,
2010-11, 2017 y 2022-24.

Es la fuente que faltaba. No depende del padrón de habilitaciones ni de que alguien haya
salido a caminar: es un relevamiento censal del uso de cada parcela, hecho por el Gobierno,
repetido cada cuatro años y con dos cortes temporales que permiten mirar variación. Para los
barrios del sur y el oeste —donde el padrón de habilitaciones es delgado— es la única fuente
que tiene la misma densidad que en el norte.

*Limitación:* clasifica por categoría de uso, y no siempre separa gastronomía de comercio en
general. Hay que ver cómo está codificado antes de contar. El relevamiento 2022-24 puede no
estar completo para todos los barrios.

### Mapa de Oportunidades Comerciales (MOC) — Desarrollo Económico, GCBA

<https://moc.buenosaires.gob.ar/> · plataforma web, sin descarga masiva confirmada

**Georreferencia: sí, por fracción censal.** Toda la Ciudad, con altas y bajas de comercios por
rubro.

Es la única fuente encontrada que tiene **bajas**. El padrón de habilitaciones no las registra
—ese es su defecto estructural, y la razón por la que su número es «direcciones que alguna vez
tuvieron habilitación» y no «locales abiertos»—. Si el MOC efectivamente da altas y cierres por
rubro y fracción, resuelve la mitad del problema de vigencia.

*Limitación:* la unidad es la fracción censal, no el barrio ni la zona, y no está confirmado
que permita exportar datos crudos. Hay que abrirlo y ver.

---

## Contraste independiente

### OpenStreetMap — extracto de Argentina (Geofabrik) y Overpass API

<https://download.geofabrik.de/south-america/argentina.html> · OSM PBF, Shapefile, GeoPackage
<https://overpass-turbo.eu/> · API, consultas por polígono

Puntos con coordenada y etiqueta (`amenity=restaurant`, `cafe`, `bar`, `fast_food`).
Actualización cada diez a dieciséis horas. Geofabrik para bajar el país entero una vez;
Overpass para consultar barrio por barrio sin descargar nada.

Es la única fuente **no estatal y no comercial** de la lista, lo que la hace valiosa
justamente como control: si OSM y las habilitaciones coinciden en una zona, el número es
sólido; si divergen mucho, hay algo para mirar.

*Limitación:* la cobertura depende de mapeo voluntario y es desigual. Es esperable que sea peor
en el sur y el oeste que en Palermo, que es exactamente donde más la necesitamos —así que su
valor es de contraste, no de conteo.

---

## Listados curados del sur, para semilla y validación

### Turismo en Barrios · Circuitos a pie — Ente de Turismo CABA

<https://turismo.buenosaires.gob.ar/es/agrupador-noticias/turismo-en-barrios-circuitos-pie>
PDF con mapa numerado y direcciones. Verificados: **Barracas, La Boca, Mataderos y Flores**.
No hay folleto propio de Nueva Pompeya, Parque Patricios, Villa Soldati, Villa Lugano ni
Liniers.

### Circuito Gastronómico de Barracas — GCBA

<https://buenosaires.gob.ar/gcaba_historico/fid/circuito-gastronomico-de-barracas>
Doce locales tradicionales con nombre y dirección. Universo chico y estático: sirve de semilla
para Barracas, no para contar el barrio.

### Dónde Comer · Distrito de Diseño (Barracas) — Subsecretaría de Inversiones

<https://buenosaires.gob.ar/gcaba_historico/distritoseconomicos/distritodediseno/mapa-distrito-de-diseno/donde-comer>
La página carga por JavaScript y no se pudo leer el listado. **Queda para revisión manual**, no
para uso automático.

### Censo Nacional Económico 2020/2021 — INDEC

<https://censoeconomico.indec.gob.ar/index.php/datos-clave/> · PDF

Sirve como techo macro para chequear plausibilidad («servicios de alojamiento y comida» a nivel
Ciudad). **No se confirmó que abra por comuna**, así que no reemplaza nada barrial.

---

## Lo que se buscó y no sirvió

- **FEHGRA y AHRCC** (cámaras del sector): no publican listado de asociados por barrio ni
  direcciones. Sólo contacto institucional. Descartadas.
- **IDECABA / IDEEC** (visualizador geoespacial de Estadística y Censos): cuatro URLs
  candidatas, todas fallaron —502, robots inaccesible, o contenido por JavaScript—. Además
  podría solaparse con F11, que ya está catalogada. Requiere revisión manual desde un navegador.
- **Anuario Estadístico de la Ciudad**, categoría Comercio Interior: timeout de conexión.
  Probablemente cae dentro de F11.

---

## Qué haría con esto, en orden

1. **Abrir el Relevamiento de Usos del Suelo** y ver cómo codifica gastronomía. Si la separa
   bien, se convierte en la fuente primaria del barrido, por encima de las habilitaciones.
2. **Entrar al MOC** y averiguar si exporta. Es lo único que resuelve el problema de vigencia.
3. **Bajar el extracto de OSM** y usarlo como tercer control en las 22 zonas ya publicadas,
   donde tenemos con qué compararlo.
4. Los circuitos del Ente de Turismo, como semilla de La Boca, Barracas, Mataderos y Flores.
