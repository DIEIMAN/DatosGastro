# Edición editable (.docx) — Atlas DGDGAS

Versión en Word de la **edición de conducción**, para que Jefatura pueda editarla
directamente. Mismo corpus cerrado R01–R22 y misma cartografía que el PDF de conducción:
ninguna cifra, geometría ni decisión territorial cambia entre uno y otro.

| Archivo | Qué es |
|---|---|
| `ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS.docx` | El entregable. 62 páginas A4, márgenes de 2 cm. |
| `ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_DOCX.pdf` | Prueba de paginación del `.docx` (ver más abajo). |
| `assets_docx/mapas_200dpi/` | Los 32 mapas exportados a PNG, 200 dpi. |
| `qa/QA_EDICION_DOCX.csv` | Los 22 controles automáticos. |
| `qa/QA_MAPAS_DOCX.csv` | Encuadre, tamaño y escala de cada mapa. |
| `qa/LECTURA_SIN_CONTEXTO.md` | La lectura completa desde el lugar de quien recibe el documento, con qué se corrigió y qué no. |
| `qa/esquema/` | Los esquemas contra los que se valida el XML del `.docx`. |

Las dos ediciones en PDF —conducción y técnica— **no se tocan**: sus hashes siguen siendo
los de `CHECKSUMS_SHA256.txt`. Este generador sólo lee: consume el contenido público en
memoria y no escribe ningún insumo. Hasta el 2026-08-05 no era cierto —dejaba el contenido
de conducción escrito en el archivo de la edición técnica—; la corrección es P-AV2-01.

## Qué tiene de distinto respecto del PDF de conducción

- **Sección nueva:** «Cómo se construyeron las zonas», con el texto que entregó la
  Dirección.
- **Índice propio en la página 2**, con las ocho secciones y las 22 zonas.
- **Una zona por página:** ficha, después su mapa, después sus mapas ampliados. En el PDF
  las fichas van de a dos.
- **Todo lo que no es el mapa es texto de Word:** títulos, fichas, pies, leyendas y la
  tabla «Las 22 zonas de un vistazo», que es una tabla real con columnas de ancho fijo.
- **Una pasada de lectura sin contexto** sobre el texto completo: 47 frases reescritas para
  que se entiendan sin conocer el proyecto, sin mover una sola cifra ni sacar una sola
  salvedad. Todas están en `REESCRITURAS`, en el generador, con la frase original como
  clave, y el registro con el motivo de cada una es `qa/LECTURA_SIN_CONTEXTO.md`.

## El índice y los números de página

El folio va abajo a la derecha en todas las páginas menos la portada: es un campo `PAGE` de
Word con resultado en caché, así que se ve un número aunque el lector no actualice los
campos, y Word lo recalcula al abrir y al imprimir.

Los folios del índice **no son texto puesto a mano**: se pagina el documento, se arma el
índice con las páginas que dio, se vuelve a paginar —porque el índice ocupa una hoja y corre
a todas las demás— y se repite hasta que los números dejan de moverse. Si no convergiera,
`armar_indice` corta con error antes que publicar un índice que mande a la página
equivocada; `indice_con_folios_reales` lo verifica después, entrada por entrada, contra la
página donde el título quedó de verdad.

El índice es texto fijo, no un campo `TOC`. Si Jefatura edita el documento y la paginación
se corre, hay que regenerar el archivo o reemplazarlo por *Referencias → Tabla de
contenido*: los títulos llevan estilos Título 1, 2 y 3 de Word, así que se genera solo.
Por el mismo motivo, en el cuerpo del texto no quedó ninguna referencia del tipo «ver
página 6».

## Validación del XML

Dos controles complementarios, y conviene saber qué cubre cada uno:

- `xml_en_secuencia_ooxml` mira el **orden** de los hijos en lo que este generador escribe.
- `esquema_xsd_ooxml` valida cada parte del paquete contra los esquemas de `qa/esquema/`:
  **qué atributos** admite y exige cada elemento. Es lo que hacía falta para ver que
  `w:zoom` venía sin su `w:percent` requerido —el orden estaba bien y el archivo era
  inválido igual—.

Los esquemas son propios: la distribución oficial de ECMA-376 no está en esta máquina y el
generador corre sin red. Cubren el subconjunto que este documento usa de verdad, y **lo que
no está declarado no valida**, así que un elemento o un atributo nuevo hace fallar el
control en vez de pasar inadvertido. Antes de validar se aplica el preproceso de
compatibilidad (`mc:Ignorable`), que es lo que hace cualquier lector conforme. Quedan fuera
del alcance `word/theme/theme1.xml` y `customXml/item1.xml`, las dos idénticas byte a byte a
la plantilla de `python-docx`, cosa que el propio control comprueba.

## Los mapas

Cada mapa se **vuelve a dibujar desde el renderer vectorial** en una caja del tamaño que
necesita el documento, y recién ahí se rasteriza a PNG. No se recorta ninguna página del
PDF: recortar es lo que partía las imágenes, porque el marco del mapa del PDF (18 × 22,7 cm)
no entra en una página de Word junto con su título y su pie.

`Vista` escala la geometría para que entre completa en la caja y la centra, así que
ensanchar la caja no achica el dibujo: agrega contexto alrededor. El encuadre se elige en
dos pasos: primero la escala máxima que entra en el área disponible de la página, y después
la caja se estira hasta una proporción cómoda (entre 0,75 y 1,18 de ancho sobre alto). Por
eso R02 y el contexto Corrientes–Abasto —horizontales— quedan con contexto arriba y abajo, y
R04, R14 y R15 —verticales— con contexto a los lados. Ninguno se recorta y ninguno se parte
entre dos páginas.

Corrección propia de esta línea: el control de bordes del renderer mide el ancho del rótulo
en horizontal aunque el rótulo salga rotado, así que un nombre de avenida casi vertical
—«Av. Intendente Bullrich» en Las Cañitas, «Av. Gral. Paz» en el mapa general— quedaba
cortado por el marco en una caja más baja que la del PDF. La corrección vive en
`build_atlas_docx.py`, no en `cartografia_vectorial_v2.py`: ese módulo produce las dos
ediciones ya publicadas y no se modifica.

## La prueba de paginación

`..._DOCX.pdf` **no lo produce Word**: esta máquina no tiene Word ni LibreOffice. Se dibuja
desde el mismo modelo de documento que escribe el `.docx`, con la misma tipografía (Calibri
del sistema, las mismas métricas que usa Word), la misma caja de texto y las mismas alturas
de imagen, e incluye el `contextualSpacing` de las listas y el «conservar con el siguiente»
de los títulos. Sirve para ver cómo quedó paginado.

La paginación no depende del motor de maquetado: cada página está delimitada por un salto
de página explícito y su contenido se mide antes de escribirlo. Las páginas de mapa
reservan 1,2 cm al pie —unos tres renglones— para elegir el alto de la imagen; en las de
texto la holgura la da el contenido, y el control `holgura_minima_por_pagina` informa
cuánta quedó en la página más llena. Aun así, conviene abrir el `.docx` en Word antes de
circularlo.

## Reproducción

Desde la raíz del repositorio, sin red:

    .venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_atlas_docx.py

`--dpi 150` baja la resolución de los mapas si hiciera falta achicar el archivo. Requiere
`python-docx` y `lxml` en el entorno; `lxml` es el que valida contra los esquemas.
