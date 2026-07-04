# Notas metodologicas - Borrador 3

Fecha: 2026-07-01. Documento interno. No es informe final. No se uso Google Places.

Estas notas explican como leer el Borrador 3 y, en particular, como interpretar la capa objetiva de
contexto sin sobreinterpretarla.

## 1. Evidencia documental vs capa objetiva

Son dos universos distintos y no se mezclan:

- **Evidencia documental.** Fuentes oficiales, periodisticas, gastronomicas y el documento semilla
  interno. Sostiene la clasificacion de cada caso (area nucleo, zona relevante, emergente, candidato,
  anexo, en espera de evidencia). Es la capa que decide el grupo.
- **Capa objetiva de contexto.** Presencia relativa por barrio y comuna derivada de F01 y F02. No
  decide el grupo. Solo acompana o matiza la lectura documental. Es contexto, no prueba.

Una senal objetiva alta no valida un caso debil; una senal baja no debilita un caso con documentacion
fuerte. La clasificacion la fija la evidencia documental y, en ultima instancia, la revision humana.

## 2. Identidad documentada vs densidad real

La identidad documentada (que un barrio o eje sea reconocido como gastronomico en fuentes) **no
equivale a densidad real** (cuantos locales activos hay y con que concentracion). Este trabajo mide
identidad y presencia registrada, no densidad. Para medir densidad harian falta una capa objetiva
validada de oferta/habilitaciones, una delimitacion territorial y una metodologia aprobada.

## 3. Por que el indice no es ranking

El `indice_senal_objetiva` es un indicador interno de 0 a 100 que expresa presencia relativa en las
fuentes disponibles respecto del maximo observado. No ordena polos por importancia ni por calidad.
Por eso:

- La tabla del Borrador 3 conserva el orden del Borrador 2 y **no** se ordena por indice.
- El indice **no se presenta solo**: siempre acompanado de la lectura prudente y de la limitacion
  territorial.
- El indice **no** se usa para subir o bajar la clasificacion de ningun caso.

## 4. Por que no valida subpolos ni corredores

La senal se calcula por barrio (F01) y por comuna (F02). Un subpolo (por ejemplo Palermo Soho o
Barrio Chino) hereda la senal del barrio contenedor (Palermo, Belgrano), que es mayor que el subpolo
y no lo distingue. Un corredor (por ejemplo Avenida Corrientes o Costanera Norte) atraviesa varios
barrios y no tiene un recorte propio en la fuente. En ambos casos, la senal del contenedor **no
valida** la unidad menor.

## 5. Por que algunos casos son no calculables

Los corredores y areas sin delimitacion territorial previa se marcan como **no calculables**:
Costanera Norte, Avenida Corrientes, DoHo / Donado-Holmberg, Avenida Caseros / Barracas, Avenida
Boedo, Federico Lacroze y Villa Pueyrredon / Avenida San Martin. Asignarles la senal de un barrio
unico produciria una comparacion falsa. Se mantienen como no calculables hasta que exista una
delimitacion territorial preliminar, aunque sea solo textual.

## 6. Por que no se uso Google Places

El trabajo debe basarse en fuentes abiertas u oficiales locales y no en APIs privadas ni datos
crudos de plataformas. No se uso Google Places ni ninguna plataforma privada como base. No se
guardaron identificadores tecnicos, place_id, credenciales ni datos crudos de terceros.

## 7. Limites de F01 y F02

- **F01 (oferta y establecimientos gastronomicos, 2823 registros).** Es oferta registrada; no prueba
  que los establecimientos sigan abiertos ni mide densidad real. Permite una lectura barrial de
  presencia registrada.
- **F02 (habilitaciones gastronomicas historicas, 44169 registros).** Mide habilitaciones aprobadas
  historicas; **no equivale a locales activos**. No se debe presentar como conteo de locales en
  funcionamiento.

Ninguna de las dos fuentes valida vigencia operativa actual.

## 8. F02 sirve para comuna, no para barrio

Segun la Fase 8 fuerte, en F02 quedan 44099 registros sin barrio util o determinado, por lo que la
lectura barrial de habilitaciones **no es robusta**. Por eso F02 se usa solo a nivel comuna, y la
lectura barrial se apoya en F01. La lectura comunal es mas estable pero menos precisa para
corredores y subpolos.

## 9. Regla operativa de uso

- La senal objetiva vive en el anexo tecnico, no en el cuerpo como dato duro.
- Si se cita, va siempre con lectura prudente y limitacion territorial.
- No se aplican cambios de clasificacion de forma automatica: toda recomendacion queda para revision
  humana.
