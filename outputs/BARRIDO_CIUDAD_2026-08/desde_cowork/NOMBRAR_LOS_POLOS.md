# Cómo se nombran los 124 polos

**6 de agosto de 2026** · Acompaña a `diccionario_nombres_uso_corriente.csv` (72 entradas).
Es la prueba 3 de `CUANDO_DOS_POLOS_SON_UNO.md` aplicada a escala: *¿tiene nombre de uso
corriente y respaldo documental propio?*

---

## 1 · Dónde está Soho · la respuesta, y confirma lo que midió el repo

**Palermo Viejo es el rectángulo entre Av. Córdoba y Av. Santa Fe, desde Av. Dorrego hasta
Av. Scalabrini Ortiz. Av. Juan B. Justo lo corta en diagonal por la mitad, y es la divisoria.**

- **Al norte de Juan B. Justo → Palermo Hollywood.**
- **Al sur de Juan B. Justo → Palermo Soho.**

Cinco fuentes independientes coinciden textualmente en esto, incluida la propia definición que
usa el GCBA en sus encuestas de consumo gastronómico.

**Y ahí está la confirmación documental de lo que la prueba 3 midió sin saberlo:**

| calles dominantes de P078 | de qué lado caen |
|---|---|
| Humboldt, Fitz Roy, Bonpland | **Hollywood** |
| (más: Ravignani, Carranza) | **Hollywood** |

**P078 es Palermo Hollywood.** La medición y el documento llegan al mismo lugar por caminos
distintos, que es la mejor situación posible.

**Dónde tiene que estar Soho:** en un polo cuyas calles dominantes sean **Serrano / Jorge Luis
Borges, Thames, Armenia, Malabia, Gurruchaga o Uriarte**, con núcleo en **Plaza Julio Cortázar
(Serrano y Honduras)** y **Plaza Inmigrantes de Armenia**. Los candidatos por tamaño son P091
(728 locales) y P065 (361). Don Julio —1 Estrella Michelin y Nº 3 de Latin America's 50 Best—
está en Guatemala 4699, en Soho, y sirve de punto de control: **el polo que contenga a Don Julio
es Soho**, salvo que el clustering lo haya partido.

### La trampa que hay que evitar al clasificar

Las calles **longitudinales cruzan Juan B. Justo y tienen tramos de los dos lados**:

> **Honduras, Gorriti, Costa Rica, Nicaragua, El Salvador, Cabrera y Guatemala son NEUTRALES.**
> Una calle sola no desambigua. Hace falta **calle + altura**, o la intersección.

Es exactamente la misma familia de error que los tres bugs del normalizador: un nombre que parece
identificar y no identifica. **Marcadores fuertes de Soho:** Serrano/Borges, Thames, Armenia,
Malabia, Gurruchaga, Uriarte. **Marcadores fuertes de Hollywood:** Humboldt, Fitz Roy, Bonpland,
Ravignani, Carranza.

Y una tercera opción que conviene tener a mano: si el clustering separa la franja entre **Guatemala
y Av. Santa Fe**, la etiqueta más segura no es Hollywood sino **Palermo Pacífico** —el entorno del
Puente Pacífico y el Distrito Arcos—.

---

## 2 · Los cuatro niveles, y la regla de elección

El diccionario clasifica cada nombre en cuatro niveles. **La regla es: gana el nivel más bajo
disponible.**

| nivel | qué es | cuántos |
|---:|---|---:|
| **1** | **normativo** — ley del GCBA con perímetro publicado | 10 |
| **2** | **oficial de facto** — ficha en Turismo BA, obra pública, señalización, APH | 16 |
| **3** | **uso corriente atestiguado** — sin respaldo oficial, pero con fuentes que lo usan | 40 |
| **4** | **DESACONSEJADO** — no atestiguado, erróneo, o refiere a algo extinguido | 6 |

Un nombre de nivel 1 es defendible sin discusión: tiene ley, artículo y perímetro. Un nombre de
nivel 3 es defendible citando quién lo usa. **Un nombre de nivel 4 no se usa nunca**, ni siquiera
si suena bien.

### Los seis desaconsejados, y por qué

| nombre | problema |
|---|---|
| **Palermo Queens** | **error de barrio**: la zona está en Villa Crespo. Invento inmobiliario de los 90 que las fuentes locales rechazan. Si hay un polo sobre Aguirre/Gurruchaga/Loyola, se llama **Villa Crespo** |
| **Calle Necochea / «la calle de las cantinas»** | **realidad extinguida**: las cantinas funcionaron hasta principios de los 80. Etiquetar una concentración *actual* con ese nombre sería un error |
| **Bajo Chacarita** | no atestiguado. El nombre con ficha oficial es **Polo gastronómico Chacarita** |
| **Distrito Arroyo** | marketing de galeristas. El nombre canónico es **calle Arroyo** |
| **Barrio de los Turcos** | fuente única y débil |
| **Esmeralda-Paraguay** | ver abajo — es un caso aparte |

### Y un hallazgo sobre el Atlas publicado

**R18 se llama «Esmeralda-Paraguay», y ninguna fuente usa ese nombre.** Se buscó y no aparece
como microzona gastronómica en ningún lado. El clúster real de Retiro está sobre **Reconquista,
San Martín, Paraguay y M. T. de Alvear entre Córdoba y Santa Fe**, y **no tiene nombre
consensuado**.

Eso no invalida la zona: la concentración existe y es de clase A, la más densa de las 22. Lo que
dice es que **el Atlas le puso un nombre descriptivo de dos calles porque no había uno**. Es una
decisión legítima y conviene declararla como tal en la V3, en vez de dejar que se lea como un
nombre que la gente usa.

---

## 3 · El sur, y el hallazgo que reencuadra todo

Esto es lo más importante que salió de la investigación.

**El sitio oficial de Turismo BA nombra cinco polos gastronómicos: Palermo Soho/Hollywood, Las
Cañitas, Puerto Madero, Recoleta y San Telmo. Ninguno en el oeste, y sólo San Telmo en el sur.**
El paper académico de referencia sobre geografía del consumo gastronómico porteño llega a la
misma lista de seis y tampoco identifica ningún polo, feria ni mercado en el sur ni en el oeste.

> **El vacío del Atlas no es un error del Atlas. Es la nomenclatura oficial completa la que no
> llega ahí.**

Eso cambia cómo se escribe la V3. La frase «no se identificaron zonas en el extremo sur» no fue
una falla de relevamiento: fue **heredar un vocabulario que no tiene palabras para el sur**. Y es
mucho más defendible decir eso —con la evidencia de que Turismo BA y la literatura académica
comparten el hueco— que pedir disculpas por una omisión propia.

### El anclaje que sí existe

**El Distrito del Deporte (Ley 5235/2014) es el único instrumento normativo que nombra territorio
en las comunas 8 y 9.** Perímetro: Av. Gral. Paz, Av. 27 de Febrero, Av. Cnel. Esteban Bonorino,
Av. Gral. F. Fernández de la Cruz, Av. Perito Moreno y Autopista Dellepiane, en ambas aceras.
Cubre Villa Soldati, Villa Lugano y Villa Riachuelo.

Si los diez polos del sur caen adentro o cerca de ese polígono, **tienen un nombre de nivel 1
disponible**, y eso resuelve el problema de nombrar lo que no tiene nombre.

Lo mismo vale para el resto del sur: **Distrito Tecnológico** (Parque Patricios, Ley 2972),
**Distrito de las Artes** (La Boca–San Telmo–Barracas, Ley 4353), **Distrito de Diseño**
(Barracas, Ley 4761). Cuatro leyes que cubren buena parte del sur con perímetros publicados.

### Y las áreas que efectivamente no tienen nombre

Se verificó una por una. **No tienen ninguna denominación de uso corriente más allá del nombre
del barrio:** Villa Soldati, Villa Riachuelo, Parque Avellaneda, Floresta, Vélez Sársfield, Monte
Castro, Versalles, Villa Pueyrredón, Agronomía, Coghlan, Saavedra, Constitución.

En Villa Lugano la gente dice «Larrazábal» o «el centro de Lugano»; en Pompeya, «Sáenz». **Son
nombres de calle, no de zona.** Cuando un polo caiga ahí y no tenga distrito normativo encima,
el nombre correcto es descriptivo y se declara como tal: *«concentración sobre Av. Larrazábal,
Villa Lugano»*, no un nombre inventado.

### Las colectividades

Cuatro enclaves con territorialización gastronómica **y nombre**: **Barrio Chino** (Belgrano,
nivel 2 — tiene arco, obra del GCBA y ficha), **Barrio Coreano / Baek-ku** (Flores, nivel 3 —
tiene portal físico pero no ley), **Barrio Charrúa** (Pompeya/Soldati, nivel 3), y el enclave
boliviano de **Liniers**, que tiene el problema inverso: **cinco nombres compitiendo**
—«microcentro boliviano», «la Pequeña Bolivia», «el altiplano de Liniers», «el Bolishopping», «la
feria boliviana»—. Hay que elegir uno; *microcentro boliviano de Liniers* es el que usa la
literatura de juntas históricas.

Las comunidades **peruana** y **paraguaya** tienen presencia gastronómica pero **sin
territorialización nombrada**: se dispersan por Abasto, Once y Bajo Flores. Eso también se
reporta — es un dato, no un faltante.

---

## 4 · El procedimiento, para los 124

Cuando llegue `POLOS_PARA_NOMBRAR.csv`, para cada polo:

1. **¿Cae adentro de un perímetro normativo?** (los 10 de nivel 1) → ése es el nombre, y se cita
   la ley.
2. **¿Sus calles dominantes coinciden con un nombre de nivel 2 o 3?** → ése, citando la fuente.
   Si coincide con más de uno, gana el de nivel más bajo.
3. **¿Coincide con un nombre de nivel 4?** → **no se usa.** Se busca la alternativa que el
   diccionario indica en la columna `nota`.
4. **¿No coincide con nada?** → nombre descriptivo: *«concentración sobre \<eje\>, \<barrio\>»*, y
   se declara en el texto que es una denominación de trabajo, no un nombre de uso corriente.

Y un campo por polo que no hay que perder: **`nivel_del_nombre`**, con el número del 1 al 4. Un
atlas donde se puede ver de un vistazo cuáles zonas tienen nombre con ley, cuáles con uso, y
cuáles con una etiqueta que inventamos nosotros, es mucho más honesto que uno donde todos los
nombres parecen igual de firmes.

---

## 5 · Tres avisos operativos

**Hay dos «La Isla».** Una en Recoleta (Las Heras, Pueyrredón, Libertador, Agüero) y otra en La
Paternal (el triángulo Warnes–San Martín–Juan B. Justo, que corresponde a R21 del Atlas).
Desambiguar siempre.

**«Microcentro» y «Área Céntrica» no son lo mismo.** Microcentro es uso corriente, ~60 manzanas.
Área Céntrica es la **Ley 6.508/2022** con otro perímetro, bastante más grande. Si se usa el
nombre oficial hay que usar el perímetro oficial.

**El Distrito del Vino tiene dos perímetros publicados** —el del texto legal y otro que circuló en
prensa al reglamentarse— y un fallo judicial de 2024 puso en riesgo su vigencia. Si un polo del
oeste cae ahí, conviene citar el artículo 2 de la Ley 6447 y no la versión de prensa.
