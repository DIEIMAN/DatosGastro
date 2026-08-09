# Hay dos proyectos de ficha, y no son el mismo

**9 de agosto de 2026 · barrido de duplicación, antes de escribir la tanda 2**

Escrito porque frené la producción en serie al encontrarlo. La auditoría de esta mañana detectó
que conviven dos numeraciones de secciones y lo atribuyó a un renumerado. **No fue un renumerado:
cambió el objeto del documento**, y hay dos líneas de trabajo completas, cada una coherente por
dentro, que nadie reconcilió.

---

## Los dos proyectos

| | **A · las 124 fichas** | **B · las 41 fichas** |
|---|---|---|
| fecha | 6 de agosto | 8 de agosto |
| objeto | las **124 concentraciones** detectadas | los **41 polos admitidos** por las seis vías |
| plantilla | `FICHA_Y_ESTRUCTURA_V3.md` | `MODELO_DE_FICHA_Y_TRES_EJEMPLOS.md` |
| ejemplos escritos | `FICHAS_DE_MUESTRA.md` — 4 fichas | el modelo — 3 fichas · `FICHAS_SECCION_VII_TANDA_1.md` — 11 |
| datos | `POLOS_NOMBRADOS.csv`, 124 filas | `fichas_corpus_polos.csv`, 48 filas |
| forma | tabla + un párrafo · se lee en 30 segundos | prosa · dos páginas |
| agrupación | **por comuna** | por origen (referencia publicada / zona nueva) |
| el cuerpo es | sección **V** | sección **VII** |
| «qué no dice» | sección **VII** | sección **IX** |

**Y no describen las mismas cosas.** Palermo Soho es el polo P091 con ficha propia en el proyecto
A, y una subzona de R01 Palermo en el B. Villa Lugano tiene ficha en A y en B es una fila de la
matriz. Las 124 salen del clustering; las 41 salen del criterio de admisión.

---

## Por qué importa antes de escribir treinta fichas más

**El proyecto A declara una decisión que el B contradice.** `FICHA_Y_ESTRUCTURA_V3.md` B.0 dice:
*«De 22 referencias a 124 polos»* y *«la V3 reemplaza a la V2. No conviven. (Decisión tomada.)»*

La restricción vigente de Diego dice lo contrario: **las 22 referencias publicadas sólo se
amplían, nunca se redefinen ni se dan de baja.** El proyecto B está construido sobre esa
restricción; el A es anterior a ella.

**No es que uno esté mal.** Es que el documento no puede tener dos cuerpos, y hoy tiene material
para los dos.

---

## Lo que el proyecto A tiene y el B perdió

Tres cosas del 6 de agosto que valen y que mis once fichas no usan:

**1 · Los nombres, ya resueltos para los 124.** `POLOS_NOMBRADOS.csv` trae `nivel_del_nombre` en
cuatro niveles, calculado: **3 normativos · 9 oficiales de facto · 38 de uso corriente · 74 de
trabajo**, estos últimos marcados con `°`. Con su `fuente_del_nombre` y su leyenda de publicación.
Ninguna de las fichas de la tanda 1 declara el nivel del nombre que usa.

**2 · El campo `límites de lectura`, que no es «lo que falta».** Son dos cosas distintas y las dos
hacen falta: *lo que falta* dice qué verificación está pendiente; *límites de lectura* dice **qué
no se puede afirmar de este polo aunque todo esté verificado**. Ejemplos reales del archivo: *«el
43 % de sus locales trae dirección, así que el ranking de ejes describe bien la zona pero no la
agota»*; *«la concentración vecina más cercana está a 75 metros: el borde es una decisión, no una
línea del terreno»*.

**3 · Dos reglas de redacción que la tanda 1 no aplica.**

- **Cada número lleva su instrumento.** «823 locales» se lee como censo; «823 locales según las
  fuentes relevadas» se lee como lo que es. Mis fichas lo dicen una vez en la nota de sección y
  eso no alcanza para una ficha que se va a leer suelta.
- **Los adjetivos de valor no entran** —no hay polos «pujantes», «consolidados» ni «emergentes»
  salvo que haya serie temporal—. La tanda 1 escribe «polo consolidado» tres veces. **Las tres son
  cita de prensa y no juicio propio**, pero conviene que se lea como cita.

Y una advertencia del proyecto A que merece estar en la sección de referentes del documento final,
venga de donde venga el cuerpo: **la densidad de hitos no mide calidad gastronómica, mide dónde
miran las guías.** MICHELIN tiene 58 restaurantes en la Ciudad y **ninguno en las comunas 4, 8 y
9**; los Bares Notables sí llegan a Mataderos, La Boca, Barracas, Nueva Pompeya y Parque Chas.

---

## Dos cosas que además hay que arreglar, y son del proyecto A

**1 · El bug del normalizador de calles sigue vivo, y ese campo se publica.**

`FICHAS_DE_MUESTRA.md` lo detectó el 6 de agosto y escribió: *«conviene arreglarlo antes de
generar las 124 fichas»*. **Medido hoy contra `POLOS_NOMBRADOS.csv`: sigue en los mismos 9 polos
de 124.** La misma calle aparece dos, tres o cuatro veces en su propio top de ejes:

| polo | lo que aparece |
|---|---|
| P001 Costanera Norte | `Costanera Rafael Obligado` (14) · `Costanera Rafael Obligado S/N` (2) · `Costanera Obligado Rafael` (1) · `Rafael Obligado Costanera` (1) |
| P015 Parque Chacabuco | `Barco Centenera` (4) · `Barco Del Centenera` (2) · `Del Barco Centenera` (1) |
| P028 Villa Pueyrredón | `Mosconi` (18) · `E Mosconi` (6) |
| P022 Saavedra | `Ricardo Balbin` (8) · `Doctor Ricardo Balbin` (6) |
| P050 Caballito | `Doctor Honorio Pueyrredon` (4) · `Honorio Pueyrredon` (2) |
| P047 Caballito | `Juan F Aranguren` (2) · `Doctor Juan F Aranguren` (2) |
| P048 y P071 Colegiales | `Cap Ramon Freire` · `Capitan Ramon Freire` |
| P072-1 Núñez | `Juana Azurduy` (2) · `Azurduy Juana` (1) |

El efecto es doble: parte el conteo de una calle en dos **y le roba un lugar del ranking a otra
calle que sí debería aparecer**. El `callejero_canonico.py` de la ronda 9 arregla esta misma
familia de bicho — **el arreglo nunca se propagó a este archivo.**

**2 · Palermo Soho tiene dos conteos distintos y hay que declarar cuál manda.**

`POLOS_NOMBRADOS.csv` dice **728 locales**. La ronda 9 midió **772 locales en 92,36 ha** para el
mismo P091. Son 44 de diferencia sobre el mismo polo. No sé cuál es correcto y no lo elijo: puede
ser distinta versión del polígono o distinta base. **Hasta resolverlo, ninguna ficha de Palermo
debería citar el conteo de la subzona**, y la ficha de la tanda 1 lo cita.

---

## La decisión, que es de Diego y no mía

Tres salidas posibles:

**(a) Las 41 en prosa como cuerpo, las 124 como capa de datos y anexo.** Es lo compatible con la
restricción de que las 22 sólo se amplían, y es donde ya hay 11 fichas escritas. Las 124 no se
tiran: se publican como tabla con sus nombres y sus polígonos, que ya están.

**(b) Las 124 tabulares como cuerpo**, que es el plan del 6 de agosto. Cubre la Ciudad entera y se
lee rápido, pero deja de haber un lugar donde contar por qué una zona entra: las seis vías no
tienen dónde vivir.

**(c) Las dos.** Sección de fichas de polo para las 41, y anexo de fichas breves para las 124. Es
el documento más completo y el más caro: son 41 fichas de dos páginas más 124 de media página.

Mi lectura, para que la tengas escrita y no para reemplazar la decisión: **(a)**. El trabajo de
las seis vías, la vigencia con fecha y la capa de memoria —que es lo que ningún otro documento del
GCBA puede hoy— sólo tiene dónde contarse en la ficha larga. Y las 124 ya están nombradas y
poligonizadas: como anexo cuestan poco y cubren el hueco geográfico.

**Lo que no conviene es seguir escribiendo sin decidir**, porque las dos formas comparten datos y
ninguna de las dos se reusa entera para la otra.
