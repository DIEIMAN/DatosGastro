# Ficha de polo y estructura del Atlas V3

**6 de agosto de 2026** · La plantilla de las 124 fichas y el esqueleto del documento.

---

# Parte A · La ficha de polo

## A.1 · El principio

Una ficha tiene que poder leerse en treinta segundos y resistir una pregunta difícil. Eso se logra
con **un orden fijo**, **campos que siempre están** —aunque digan «no corresponde»— y **la
incertidumbre adentro de la ficha, no en un anexo**.

Regla que atraviesa todo: **ningún campo se deja en blanco.** Un campo vacío se lee como «no hay»;
un campo que dice explícitamente qué falta se lee como lo que es.

## A.2 · Los campos, en orden

### Encabezado

| campo | contenido | qué hacer si falta |
|---|---|---|
| `nombre` | el nombre de uso corriente | denominación de trabajo descriptiva |
| `nivel_del_nombre` | 1 normativo · 2 oficial de facto · 3 uso corriente · 4 de trabajo | nunca falta |
| `fuente_del_nombre` | ley y artículo, ficha, o «denominación de trabajo» | nunca falta |
| `barrios` | con conteo: «Palermo (210); Villa Crespo (44)» | nunca falta |
| `comunas` | | nunca falta |
| `polo_id` | el id del borrador, que se conserva | nunca falta |

### El cuerpo

| campo | contenido | nota |
|---|---|---|
| `locales` | conteo | **es lo que ven siete fuentes, no un censo** |
| `superficie_ha` | del polígono publicado | |
| `densidad` | locales/ha | |
| `clase_densidad` | A · densa / B · media / C · extendida | **va con `distancia_al_corte`** |
| `distancia_al_corte` | cuán cerca está del corte de clase | las clases son lectura, no propiedad (Rand 0,391) |
| `ejes` | hasta 6 calles dominantes, por conteo | |
| `pct_con_direccion` | qué fracción de los locales tiene dirección | **es la calidad del dato de ejes** |

### La relación con lo publicado

| campo | contenido |
|---|---|
| `zona_publicada` | qué referencia del Atlas V2 cae encima, y con qué % de solape |
| `relacion` | `coincide` · `desborda` · `parte de` · `sin correspondencia` |
| `nota_de_correspondencia` | una línea cuando la relación no es uno a uno |

**Este bloque es el que más se va a mirar**, porque es el que dice qué cambió entre la V2 y la V3.
Y ya sabemos que la correspondencia **no es uno a uno en ninguna de las dos direcciones**: R01
contiene 1.358 locales de los cuales sólo 306 son de P078, y 279 de los 585 de P078 (47,7 %) caen
fuera de R01.

### Los hitos

| campo | contenido |
|---|---|
| `hitos_n` | cuántos caen adentro |
| `hitos_destacados` | hasta 5, ordenados: Estrellas Michelin → posición 50 Best → bar notable → resto |
| `hitos_fuente` | la cita, siempre |

**Y una advertencia que va escrita una vez en el Atlas, no en cada ficha:** la densidad de hitos
no mide calidad gastronómica, mide **dónde miran las guías**. Michelin tiene 58 restaurantes en
CABA y ninguno en las comunas 4, 8 y 9; los bares notables sí llegan a Mataderos, La Boca,
Barracas, Nueva Pompeya y Parque Chas. Un polo con muchos bares notables y cero Michelin no es un
polo peor: es un polo que las guías no visitan.

### Y el campo que hace la diferencia

| campo | contenido |
|---|---|
| **`limites_de_lectura`** | **una a tres líneas sobre qué NO se puede afirmar de este polo** |

Ejemplos de lo que va ahí, tomados de casos reales:

> *La cobertura de la base en este barrio (2,30) está en el percentil 10 de la Ciudad. Sobre la
> extensión de este polo no se concluye nada.*

> *Este polo está al filo del corte de clase: 0,08 loc/ha lo separan de la clase B.*

> *La partición en tres partes se evaluó y se rechazó por inestable; se publica entero.*

> *El nombre es una denominación de trabajo: no se encontró un nombre de uso corriente para esta
> concentración.*

Un polo cuyo `limites_de_lectura` diga «ninguno relevante» es raro y debería dar sospecha.

## A.3 · Cómo se escribe · las tres reglas de redacción

**1 · «No encontramos» no es «no existe».** Rige en cada ficha, no sólo en la introducción.

**2 · Cada número lleva su instrumento.** «212 locales» sin más se lee como censo. «212 locales
según las siete fuentes relevadas» se lee como lo que es. En la ficha alcanza con decirlo una vez,
en el encabezado del bloque.

**3 · Los adjetivos de valor no entran.** No hay polos «pujantes», «consolidados» ni
«emergentes» salvo que haya una serie temporal que lo sostenga — y no la hay. Hay polos densos y
polos extendidos, que es lo que medimos.

---

# Parte B · La estructura del Atlas V3

## B.0 · Qué cambia respecto de la V2

Tres cosas, y conviene que estén en la primera página:

1. **De 22 referencias a 124 polos**, cubriendo toda la Ciudad.
2. **La V3 reemplaza a la V2.** No conviven. (Decisión tomada.)
3. **El método está publicado**, con sus sensibilidades y sus controles fallidos.

## B.1 · El esqueleto

**I · Presentación** (2–3 pág.)
Qué es este atlas, para quién, y qué decisión permite tomar que antes no se podía.

**II · Qué es un polo gastronómico** (3–4 pág.)
Que no es una entidad natural sino una categoría de lectura, y que por eso lo que se ofrece es una
decisión reproducible y no una verdad. **Las cuatro familias** —polo, multiparte, eje o corredor,
referencia dispersa— y cómo se verifica cada una. Es la sección que evita el 90 % de las
discusiones posteriores.

**III · De dónde salen los datos** (4–5 pág.)
Las siete fuentes, los **cinco grupos de independencia**, y por qué contar fuentes en vez de
grupos es un error. Las licencias y qué se puede publicar de cada una. **La corrección de los
asientos replicados (22,6 %)**, porque cambia la palabra «habilitaciones» por «trámites» en todo
el documento. Y el rol de Google Places: descubre, no enumera, y no confirma vigencia.

**IV · Cómo se leyó el territorio** (4–6 pág.)
El barrido, el mínimo de 40 anclado en la zona publicada más chica, las tres pruebas de
continuidad con los precedentes de Recoleta y Belgrano, y el hallazgo del hull: **toda decisión
de unir se toma entre puntos**. Con las curvas, no sin ellas.

**V · La Ciudad, comuna por comuna** (el grueso)
Las 124 fichas, agrupadas por comuna y no por ranking. **Agrupar por comuna y no por tamaño es una
decisión editorial con consecuencia política:** un atlas ordenado por cantidad de locales pone
Palermo primero y el sur al final, y reproduce en el índice exactamente el sesgo que el trabajo
vino a corregir.

**VI · Lo que se midió y no alcanzó** (3–4 pág.)
El registro de candidatos bajo el mínimo, con su tabla de sensibilidad. El saliente N–NE. Las
zonas publicadas que no se reencontraron, con la taxonomía E1/E2/E3. **Es la sección que vuelve
honesta cualquier afirmación de ausencia**, y es la que la V2 no tenía.

**VII · Qué no dice este atlas** (2 pág.)
Los límites de la Parte X de la edición técnica: no dice cuántos locales hay, no dice si están
abiertos, no alcanza a lo que no tiene registro, y el número de polos depende de los parámetros.

**VIII · Nota metodológica** (2–3 pág.)
Resumen, con remisión a la **edición técnica** como documento aparte.

**Anexos:** tabla completa de los 124 · correspondencia V2 → V3 · glosario · fuentes y licencias.

## B.2 · Las cinco decisiones editoriales que hay que tomar antes de escribir

1. **¿Los mapas van por comuna o hay un mapa general desplegable?** (Sugerencia: los dos. El
   general es el que se va a fotografiar.)
2. **¿Las fichas llevan foto?** Si sí, hace falta un criterio de qué se fotografía que no
   privilegie lo pintoresco — o el sur vuelve a quedar mal parado.
3. **¿Se publica la capa de datos junto con el documento?** Es lo que convierte esto en una base
   utilizable por terceros, que era el objetivo declarado. Requiere resolver licencias por campo.
4. **¿La V3 se numera desde cero o conserva los R01–R22?** (Sugerencia: conservar la
   correspondencia en un anexo y numerar desde cero, porque la relación no es uno a uno.)
5. **¿Quién firma qué?** La edición técnica y el atlas tienen lectores distintos y podrían tener
   autorías distintas.

## B.3 · Qué está listo y qué falta

| pieza | estado |
|---|---|
| método, entero | **listo** — edición técnica escrita |
| criterios de lectura y poligonización | **listo** |
| regla de unión y partición | **listo**, con la cuarta regla del hull para agregar |
| capa de hitos documentales | **listo** — 199 filas, falta geocodificar |
| diccionario de nombres | **listo** — 72 entradas en cuatro niveles |
| plantilla de ficha | **listo** — este documento |
| texto de las secciones I–IV y VII | **listo** — `ATLAS_V3_SECCIONES_I_IV_VII.md` |
| los 124 nombres | **falta** `POLOS_PARA_NOMBRAR.csv` |
| polígonos publicables | **en curso** en el repositorio |
| las 124 fichas | **falta** — depende de las dos anteriores |
| secciones V, VI y VIII | dependen de las fichas |
