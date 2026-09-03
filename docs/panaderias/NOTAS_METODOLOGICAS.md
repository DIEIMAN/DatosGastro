# Panaderías — notas metodológicas

Corrida del 2026-08-27. Leer antes de citar cualquier número.

## Qué se hizo

Réplica de la línea de Casas de Pastas sobre fuentes públicas locales: inventario de
fuentes, extracción de candidatos con trazabilidad fila a fila, clasificación A/B/C,
deduplicación a un maestro de establecimientos, geocodificación desde la caché local,
asignación de comuna y barrio por geometría oficial, tablas de conteo y densidad,
habilitaciones por año y figuras.

No se usó Drive, ni fuentes internas, ni scraping, ni ninguna API paga.

## Resultado

Cifras del 2026-08-28, **contando por habilitación** (fase F1 cerrada). El día anterior,
con el lector de F02 ya corregido pero agrupando por partida matriz, eran 1.176 / 471 /
1.647; y la primera corrida del 27 publicó 569 / 77 / 646, porque leía mal siete de los
ocho archivos de la fuente. Ver `docs/estudios_de_rubro/IMPACTO_LECTOR_2026_08_27.md` y,
más abajo, "Deduplicación".

| Universo | Establecimientos | Geolocalizados |
|---|---|---|
| A — núcleo (elabora o despacha pan) | 1.219 | 1.203 (98,7 %) |
| B — punto de cocción y probables | 513 | 503 |
| **A + B** | **1.732** | 1.706 |

Las cifras de geolocalización son posteriores a la corrida de USIG de la tarde del
2026-08-27, que llevó la cobertura del universo A de 65,4 % a 99,1 %. El control de esa
geocodificación está en `outputs/panaderias/analisis/d8_qa_geocodificacion.csv`.

Composición del universo A por rubro:

| Patrón | Establecimientos |
|---|---|
| `elaboracion_panaderia_venta_directa` | 676 |
| `despacho_de_pan` | 448 |
| `elaboracion_panaderia_ncp` | 59 |
| `elaboracion_industrial_panaderia` | 36 |

**Esto importa:** 448 de los 1.219 son "Com.Min. despacho de pan y productos afines", que
es un rubro de venta. Los otros 771 declaran elaboración. Si lo que se quiere contar es
"dónde se hornea pan", el número es 771, no 1.219. La tabla de arriba tiene que acompañar
a cualquier cifra que se publique.

Vale la pena notar el vuelco: con el lector roto, el despacho de pan era el 88 % del
universo A y la elaboración parecía una rareza (71 casos). Leídos los ocho archivos, la
elaboración es mayoría. La conclusión que se sacaba del padrón anterior era, además de
chica, equivocada de signo.

## Hallazgo: F02 son ocho archivos con tres formatos distintos

Los ocho archivos de F02 no comparten formato. Cambian el delimitador, la codificación y
los nombres de columna:

- `f02_habilitaciones_aprobadas_2025.csv` — delimitador coma, UTF-8, columnas
  `razon_social`, `rubro`, `domicilio`, `comuna`, `nropartidamatriz`, `disposicion`.
- Los otros siete (2015-2018 a 2024) — delimitador `;`, columnas `descripcion_rubro` /
  `DescripcionRubro`, `calles`, `partida_matriz`, `fecha_habilitacion`, con la caja de los
  nombres cambiando según el año. El de 2021 arrastra 588 columnas `Unnamed`. Seis de esos
  siete son UTF-8; sólo el de 2024 es cp1252, y el de 2022 trae doble codificación adentro.

El lector heredado de `build_casas_pastas.py` abría todos con delimitador coma: sobre los
siete viejos eso produce una única columna, ninguna de las columnas buscadas existe, y
**el archivo entero aporta cero filas sin emitir ningún error**. Corregido el delimitador,
aparece el segundo error: forzar latin-1 rompe los acentos justo en la nomenclatura
moderna (`ELABORACIÓN DE PRODUCTOS DE PANADERÍA` queda como
`elaboraci n de productos de panader a`) y ningún patrón la reconoce.

Cada error tiene su cuota: con el delimitador corregido pero la codificación forzada a
latin-1, el universo A da 569; corregidas las dos cosas, da **1.176** contando por
inmueble y **1.219** contando por habilitación.

La lectura ya no vive en este subproyecto: está en `scripts/shared/fuentes_locales`, con
detección de dialecto por archivo y pruebas de regresión en `tests/test_fuentes_locales.py`.
**Esto alcanzaba también a Casas de Pastas**, cuyo universo A pasa de 10 a 139; sus
salidas no se tocaron y la decisión de regenerarlas es de Diego.

## Límites

1. **F02 son habilitaciones.** Registros administrativos, no locales activos. Una
   habilitación vigente en el archivo puede corresponder a un local cerrado hace años.
2. **La serie por año no es una serie.** El archivo 2025 no trae fecha de habilitación
   (el año se infiere de la disposición, que devuelve 2015-2018), así que **no hay ninguna
   habilitación posterior a 2024** en el proyecto. Y el archivo 2023 tiene 5.063 filas
   contra 12.938 de 2020 o 26.430 de 2022: su caída es de la fuente, no del rubro. La
   tabla `panaderias_habilitaciones_por_anio.csv` sirve para ver de dónde viene cada
   registro, no para leer una tendencia.
3. **16 de los 1.219 del universo A no tienen comuna.** Eran 389 antes de la corrida de
   USIG. Las direcciones que siguen sin resolver casi no tienen altura (esquinas, S/N) y
   USIG no las resuelve solas. Las tablas por comuna y barrio suman 1.203, no 1.219:
   siguen siendo cotas inferiores, pero por 16 casos, no por 389.
4. **1.615 de los 1.732 registros no tienen nombre.** Ver privacidad, abajo.
5. **F01 aporta prácticamente nada:** 1 registro, de nivel B. No tiene categoría
   panadería; su categoría más cercana es confitería, que está fuera del alcance.
6. **El padrón no es el universo de la Ciudad.** Los ocho archivos suman 391.046 filas y
   40.634 partidas matriz distintas de todos los rubros. No son el padrón de habilitaciones
   de CABA: son el recorte que hay descargado en `data/raw`. 1.219 panaderías es lo que
   estas fuentes ven, y hay que decirlo así, sin presentarlo como el total de la Ciudad.

## Privacidad

Los archivos viejos de F02 traen `titulares` y `cuits`. Son personas físicas y CUIT, y el
guardrail 7 los prohíbe. **El lector no abre esas dos columnas.** El costo es que las
filas de esos archivos quedan sin nombre de establecimiento y se identifican por partida
matriz y domicilio: 1.615 de 1.732 registros. Poner nombre exige otra fuente, no ese campo.
Los 117 que sí tienen nombre salen del padrón 2025, y desde F1 ese nombre se conserva
aunque el representante del grupo sea una fila vieja que no lo trae.

Queda una cuestión abierta: en el archivo 2025 el campo `razon_social` a veces es una
persona física (por ejemplo "María Del Carmen Andrade Tedin y Raúl..."). Se conservó
porque es el nombre comercial de la habilitación y porque Casas de Pastas ya lo publica
así, pero si estas salidas van a salir del ámbito interno hay que revisarlo.

## Deduplicación

F02 está desnormalizado: una fila por rubro × domicilio × trámite. Un solo local llega a
aparecer cien veces, y el grupo más grande del maestro reúne 362 filas crudas. La clave de
agrupamiento es, en este orden:

1. **La habilitación**: `solicitud` (más unidad funcional) en los siete archivos viejos y
   `disposicion` en el de 2025. Cubre el 99,7 % de los establecimientos.
2. Partida matriz + nombre normalizado, cuando no hay ninguna de las dos.
3. Nombre + calle sin altura, y en último lugar el domicilio completo con altura — así una
   calle entera no colapsa en un solo establecimiento.

**Por qué la habilitación y no la partida.** La partida matriz identifica el inmueble: el
51 % de los inmuebles del universo aloja más de una habilitación, así que agrupar por
partida fusiona locales distintos de un mismo edificio. Contando por habilitación, el
universo A pasa de 1.176 a 1.219.

Tres cosas hubo que resolver para que el cambio no rompiera otras:

- **La misma habilitación publicada dos veces.** El padrón 2025 vuelve a publicar trámites
  viejos, y como el archivo legacy se identifica por `solicitud` y el moderno por
  `disposicion`, el mismo local entraba dos veces. Se unen cuando coinciden partida,
  domicilio y año y hay exactamente un grupo de cada lado: 59 casos del universo A. Quedan
  2 ambiguos sin unir, a propósito.
- **379 solicitudes aparecen en dos archivos** porque los años se solapan, y las 379 traen
  el mismo domicilio: son la misma habilitación publicada dos veces, y agrupar por
  solicitud las une, que es lo correcto.
- **El nombre no se pierde al fusionar.** Si el representante del grupo es una fila vieja
  sin nombre y otra fila del mismo trámite lo tiene, se completa. Sin eso, la cobertura de
  nombres caía de 119 a 38.

**El precio, medido.** Un local habilitado dos veces —renovación, cambio de titular— son
dos habilitaciones y entra dos veces. La cota superior es **83 establecimientos, el 6,8 %
del universo A**: 81 domicilios donde conviven dos registros con el mismo patrón de rubro,
80 de ellos con una sola partida. La lista está en
`outputs/panaderias/analisis/d9_renovaciones_candidatas.csv` y se resuelve mirándola, no
con una regla: dos panaderías pegadas son igual de compatibles con la evidencia que una
sola habilitada dos veces.

559 registros salen marcados con `requiere_revision_manual = si`: todo el universo B, los
rubros industriales o de panificadora del A, y los que no tienen geo. Eran 898 antes de la
geocodificación, que resolvió la mayor parte de la tercera causa.
