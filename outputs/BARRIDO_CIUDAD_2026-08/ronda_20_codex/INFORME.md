# Verificación complementaria de locales y consistencia de registros

## Resultado que cambia

La cobertura documental fechada mejora en cuatro casos: **Makarios** avanza de 2023-06-19 a 2024-02-17 y el bloque histórico pasa de **48/54 a 51/54** por **El Estaño 1880**, **Bar Bidou** y **Boston City**. La evidencia es de nivel v2: acredita existencia o actividad a la fecha de cada fuente, no atención al 10 de agosto de 2026.

Además, la duda de domicilio de Saverio queda resuelta administrativamente: San Juan 2809 y 2816 corresponden a parcelas diferentes. El cruce de registros detecta 19 variantes de nombre entre catálogo y capa, dos domicilios desactualizados o erróneos y 11 grupos repetidos por nombre dentro de la capa de reconocimientos.

Fecha de revisión: **2026-08-10**. No se usaron APIs pagas ni datos personales.

## 1. Locales de Flores, Villa Luro y Donado–Holmberg

Se revisaron 15 casos. El único avance con una pieza pública fechada posterior al antecedente fue Makarios: una nota del **2024-02-17** individualiza nombre, oferta y **Felipe Vallese 3130** ([fuente](https://www.c5n.com/lifestyle/la-parrilla-buenos-aires-comer-asados-economicos-y-muy-ricos-n146679)). El resultado se registra como `abierto_a_fecha_fuente`, no como abierto al corte.

Los otros 14 permanecen en `vigencia_no_verificada`: los nueve del registro kosher sólo conservan la prueba oficial de **2015** ([listado oficial](https://turismo.buenosaires.gob.ar/sites/turismo/files/establecimientos_KOSHER_2015_0.pdf)); Estación de Milanesas, García Restaurante, Mich Bar y Pulpería Norte no obtuvieron una pieza editorial posterior a 2023; Cimino R no obtuvo una pieza posterior a 2022 que acredite la sede de Donado 1919. El permiso municipal de Cimino y los estados de agregadores se registraron como indicios, pero no se convirtieron en veredictos.

El CSV de verificación deja por fila las consultas exactas, lo encontrado, las superficies insuficientes y el límite de cada conclusión. En ningún caso “no localizado” se interpreta como inexistente o cerrado.

## 2. Seis históricos que seguían pendientes

Tres casos alcanzan v2:

- **El Estaño 1880**: una guía oficial nacional publicada el **2025-03-25** lo describe en presente, informa oferta y actividades y consigna Aristóbulo del Valle 1100 ([fuente](https://www.argentina.travel/novedades/cafes-notables-de-buenos-aires-donde-el-sabor-se-encuentra-con-la-historia)).
- **Bar Bidou**: una pieza periodística del **2025-11-16** lo individualiza en Av. Roque Sáenz Peña 858 ([fuente](https://www.infobae.com/sociedad/2025/11/16/cafetines-de-buenos-aires-el-bar-notable-que-desafio-la-cuadricula-portena-y-la-historia-secreta-de-la-avenida-diagonal-norte/)).
- **Boston City**: una programación oficial del **2026-02-02** lo incluye en un recorrido cultural; la identidad y Florida 165 local 3 se controlaron contra el catálogo oficial firmado el **2026-02-26** ([programación](https://buenosaires.gob.ar/gcaba_historico/noticias/verano-notable-musica-literatura-y-recorridos-culturales-en-los-bares), [catálogo](https://documentosboletinoficial.buenosaires.gob.ar/publico/PE-RES-MCGC-MCGC-1225-26-ANX.pdf)).

Siguen pendientes Bar del Alvear Palace Hotel, Petit Colón y El Coleccionista. En los tres, el catálogo oficial de **2026-02-26** confirma pertenencia y domicilio, pero no operación. Para el primero predominan una página general del hotel sin fecha y piezas sobre otros espacios del edificio; para Petit Colón, una ficha sin fecha, agregadores y una agenda de 2026 que reproduce un expediente de 2023; para El Coleccionista, agregadores con fechas de actualización, fichas sin fecha y registros patrimoniales. El archivo `seis_pendientes.csv` detalla qué se buscó y qué evidencia faltaría.

## 3. Saverio: 2809 frente a 2816

La consulta al normalizador municipal asignó a Av. San Juan el código de calle **20040**. Con ese código, el servicio catastral por puerta devolvió:

| Puerta | SMP | Partida matriz | Coordenadas planas |
|---|---|---:|---|
| Av. San Juan 2809 | 30-083-040A | 186130 | 105414.133363, 100588.295872 |
| Av. San Juan 2816 | 30-082-004A | 182937 | 105450.145098, 100575.130453 |

Las puertas están separadas aproximadamente **38 metros** y tienen SMP y partida matriz distintos. Por lo tanto, no son dos accesos catastrales del mismo inmueble: son parcelas diferentes, en lados opuestos de la avenida. La conclusión se apoya en consultas municipales realizadas el **2026-08-10** ([2809](https://ws.usig.buenosaires.gob.ar/geocoder/2.2/smp?cod_calle=20040&altura=2809), [2816](https://ws.usig.buenosaires.gob.ar/geocoder/2.2/smp?cod_calle=20040&altura=2816)). `saverio_fuente_municipal.csv` conserva la respuesta mínima necesaria.

Esta resolución es catastral. No fija por sí sola la fecha de una eventual mudanza ni acredita operación comercial en ninguna puerta.

## 4. Cruce de los cuatro conjuntos

Universos controlados el **2026-08-10**: catálogo vigente de 90 establecimientos; capa de 215 objetos, todos con geometría; nueve locales nombrados en páginas periodísticas; y diez establecimientos del registro kosher, incluido Matok. Los dos últimos grupos no presentan coincidencias ocultas por nombre normalizado o domicilio con el catálogo de 90 ni con la capa de 215.

El archivo `cruce_de_los_cuatro_conjuntos.csv` contiene 32 hallazgos auditables:

- **19 nombres distintos en el mismo domicilio** entre catálogo y capa. Diecisiete son variantes o alias; Museo Fotográfico Simik/Cafe Palacio es un renombre confirmado y El Boliche de Roberto/12 de octubre es un alias del mismo establecimiento.
- **Dos conflictos de domicilio entre conjuntos**: Café Roma figura correctamente en Olavarría 409 en el catálogo y en H031, mientras H032 conserva la fusión errónea “Café Roma / San Luis 3101”; La Academia figura en Montevideo 341 en el catálogo, pero H060 conserva Av. Callao 368.
- **11 grupos repetidos por nombre dentro de la capa**. Ocho son establecimientos con más de un reconocimiento y el mismo domicilio; Don Julio tiene tres registros. Los otros tres requieren trato explícito: Café Roma es un duplicado erróneo, Crizia presenta un conflicto temporal de domicilio y Miramar es un par intencional del mismo local en ochava con dos reconocimientos y dos direcciones.

La acción recomendada no es borrar reconocimientos: es separar `establecimiento_id` de `reconocimiento_id`, marcar pares y alias, y corregir las dos filas obsoletas antes de volver a contar establecimientos o medir cobertura espacial.

## Pendientes finales

Quedan **14/15** locales sin nueva prueba fechada y **3/6** históricos sin pieza individual fechada. Se mantienen como pendientes porque las búsquedas devolvieron directorios, agregadores, páginas sin fecha editorial o actos normativos que no acreditan actividad. Para cerrarlos haría falta una actividad oficial fechada, una pieza periodística individual con domicilio o una constatación directa documentada.

No se modificaron fuentes originales, datos crudos, pipelines ni archivos de otras entregas. Los archivos producidos no contienen correos, teléfonos, identificadores técnicos de plataformas privadas, enlaces privados ni claves.
