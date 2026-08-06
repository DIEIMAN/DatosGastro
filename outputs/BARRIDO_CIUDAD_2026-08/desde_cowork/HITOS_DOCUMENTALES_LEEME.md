# Capa documental de hitos gastronómicos · CABA

**6 de agosto de 2026** · Producida afuera del repositorio, para que adentro se geocodifique y se
una a los 124 polos del borrador.

Archivo: `hitos_documentales_caba.csv` · **199 filas · 189 establecimientos únicos**

---

## Qué es

Una fila por **(establecimiento, distinción)**, no una fila por establecimiento. Un local puede
tener varias: Don Julio aparece tres veces —Michelin 1 Estrella, Latin America's 50 Best Nº 3,
World's 50 Best Nº 10—. La columna `clave_dedup` agrupa las filas del mismo local.

**9 establecimientos** tienen más de una distinción. Ésos son, casi por definición, los hitos que
más peso deberían tener en la ficha de un polo.

## Las seis capas

| tipo | filas | fuente | licencia | confianza |
|---|---:|---|---|---|
| `bar_notable` | **90** | Catálogo consolidado RES-MCGC-3758-24, Boletín Oficial CABA | documento oficial GCBA | 88 alta · 2 media |
| `michelin` | **58** | Guía MICHELIN Buenos Aires & Mendoza **2026** (fichas ViaMichelin) | Michelin, propietaria | alta |
| `ranking_internacional` | **16** | The World's 50 Best (sitio oficial) | no redistribuible | alta |
| `pizzeria_emblematica` | **20** | APYCE + Min. Desarrollo Económico GCBA | no redistribuible | 10 media · 10 baja |
| `heladeria_historica` | **5** | AFADHYA (cámara privada) | no redistribuible | baja |
| `mercado_o_patrimonio` | **10** | GCBA / Gob. Nacional / Boletín Oficial | documento oficial | 3 alta · 5 media · 2 baja |

**Sobre licencias.** Ninguna de estas fuentes es CC-BY. **Ninguna se redistribuye**: lo que entra
al Atlas es el **hecho** —este local tiene esta distinción— con la cita de la fuente, no el texto
descriptivo de Michelin ni de 50 Best. Es la misma lógica del nivel `agregado` que se usó con
Places.

---

## Lo que hay que saber antes de usarla

**1 · 27 filas no tienen dirección.** Las 20 pizzerías emblemáticas y las heladerías vienen sin
altura: hay nombre y barrio. Hay que geocodificar por nombre + barrio contra la base, y **si no
resuelve a un único local, se descarta esa fila** — no se elige la más probable.

**2 · Un conflicto de dirección detectado, y es real:**

| local | ViaMichelin | 50 Best |
|---|---|---|
| **Crizia** | Fitz Roy 1819 | Gorriti 5143 |

Las dos direcciones están cargadas, cada una con su fuente. Hay que resolverlo contra la base y
dejar la que corresponda; puede ser una mudanza o un segundo local.

**3 · La Guía Michelin 2026 es de julio de 2026.** Es la tercera edición argentina (2023, 2025,
2026). De los 89 restaurantes argentinos, **58 son de CABA**: 1 con dos Estrellas (Aramburu), 4
con una (Don Julio, Trescha, Crizia y **Han**, nueva), 11 Bib Gourmand y 42 Recomendados.

**Kobito quedó afuera a propósito**: Michelin lo lista bajo la selección «Buenos Aires» pero está
en San Isidro, Provincia. Lo mismo con Alo's, que figura en Latin America's 50 Best 2025 como
«Buenos Aires» y está en Boulogne. **Dos casos donde la fuente dice Buenos Aires y no es CABA.**

**4 · Las Estrellas Verdes 2026 no están.** Michelin declara 11 en total y ninguna fuente
accesible publica el listado. En 2025 las porteñas eran Alcanfor, Anchoíta, Crizia, Don Julio y
El Preferido — **no se cargaron**, porque no se pudo confirmar para 2026. Es un faltante conocido,
no un cero.

**5 · Bares notables: la aritmética que no cierra en la prensa.** Los medios anunciaron «12 nuevos
bares notables» en agosto de 2026, pero **10 de esos 12 ya estaban en el catálogo oficial de
2024**. Sólo Josephina's Café y Confitería El Greco son altas nuevas — y son las dos únicas filas
de esta capa que **no** tienen respaldo en el Boletín Oficial. El total de 90 coincide con lo que
informan las tres fuentes periodísticas.

**No hay dataset de bares notables en data.buenosaires.gob.ar.** Se buscó. La licencia CC-BY-2.5-AR
**no aplica** acá.

**6 · El año de declaración falta en 88 de 90.** Ningún documento oficial lo consigna: el catálogo
tiene número, nombre, dirección, barrio y comuna, y nada más. Sólo se pudo datar la tanda de 2026.

**7 · El catálogo oficial tiene inconsistencias propias**, anotadas fila por fila en `nota`:
comunas mal asignadas (Roma del Abasto, La Academia, Miramar), Café San Bernardo sin comuna,
Esquina Homero Manzi sin barrio. **No se corrigieron en silencio**: el valor está corregido en
`barrio` y la discrepancia queda en `nota`.

**8 · Bajas históricas no verificadas.** Comparando con el listado de Turismo de 2015 (~89
establecimientos), desaparecieron del catálogo actual Bar Iberia, Café Montserrat, Confitería del
Hotel Castelar, La Embajada, Victoria, La Perla de Once, Café Retiro, El Preferido de Palermo y
varios más. **Algunos cerraron y otros pueden haber perdido la condición; no hay fuente oficial
que lo aclare caso por caso**, así que no están en esta capa y no se afirma que hayan cerrado.

**9 · Lo que se buscó y no existe.** No hay ninguna ley ni normativa del GCBA que declare «polos»
o «distritos gastronómicos». Lo que existe es el programa BA Capital Gastronómica con su listado
de mercados y patios, que es administrativo, no normativo. **Es un dato relevante para el Atlas:
los polos que estamos mapeando no tienen contraparte normativa.**

---

## Cómo usarla en la ficha de un polo

Tres campos, no más:

- **`hitos_n`** — cuántos hitos caen adentro del polígono.
- **`hitos_destacados`** — hasta cinco, ordenados por peso: Estrellas Michelin, luego posición en
  50 Best, luego bar notable, luego el resto. Los 9 con más de una distinción van primero.
- **`hitos_fuente`** — la cita, siempre. Un hito sin fuente citada no entra.

**Y una advertencia de lectura que conviene escribir en el Atlas.** La densidad de hitos **no** es
una medida de calidad gastronómica de un polo: es una medida de **dónde miran las guías**. Michelin
tiene 58 restaurantes en CABA y **ninguno** en las comunas 4, 8 ni 9. Los bares notables, en
cambio, sí llegan a Mataderos, La Boca, Barracas, Nueva Pompeya y Parque Chas — porque el criterio
es histórico, no de crítica.

Cruzar las dos capas es más interesante que cualquiera de las dos por separado: **los polos del
sur tienen hitos patrimoniales y no tienen hitos de guía**, y eso es un hallazgo sobre el
instrumento tanto como sobre el territorio.
