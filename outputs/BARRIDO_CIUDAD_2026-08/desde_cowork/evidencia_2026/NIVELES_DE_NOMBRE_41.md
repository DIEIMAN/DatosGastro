# El nivel del nombre de las 41 · propuesta para firma

**9 de agosto de 2026**

El molde de ficha del 6 de agosto pide un campo que el molde del 8 perdió: **con qué autoridad se
llama a cada polo como se lo llama.** Está calculado para las 124 concentraciones en
`POLOS_NOMBRADOS.csv` y **no existe para las 41**, porque los dos universos no comparten
identificadores: `POLOS_NOMBRADOS.csv` sólo tiene P-ids y ni una referencia a los R.

**El cruce automático no sirve y lo probé.** Cruzar por nombre contra
`diccionario_nombres_uso_corriente.csv` cubre 17 de 41 y devuelve falsos positivos: da «Palermo ·
nivel 1 · normativo» cuando el propio corpus dice que Palermo no tiene anclaje normativo
gastronómico. El match cae sobre el Distrito Audiovisual, que incluye a Palermo entre sus barrios.

Lo que sigue es una asignación hecha a mano, con la evidencia al lado. **Cada fila dice en qué se
apoya, así que se puede discutir una sin tocar las demás.**

---

## La regla que apliqué, porque sin ella la tabla no se puede auditar

**El nivel califica al nombre de la referencia, no al objeto que nombra.**

Casi todas las 41 llevan nombre de barrio, y los barrios de la Ciudad están fijados por norma. Si
eso bastara para el nivel 1, treinta y cinco filas serían normativas y el campo no distinguiría
nada. Entonces:

| nivel | cuándo | ejemplo |
|---|---|---|
| **1 · normativo** | una norma con perímetro nombra **específicamente esa zona** como lo que la ficha dice que es | Distrito Tecnológico, Ley 2972/2008 |
| **2 · oficial de facto** | una ficha oficial, una obra pública o un programa del GCBA la nombra así, sin ley con perímetro | «Polo gastronómico Chacarita» |
| **3 · uso corriente** | la Ciudad lo llama así, con o sin respaldo | Palermo · San Telmo · DoHo |
| **4 · de trabajo** | no se encontró denominación de uso corriente; el nombre es descriptivo | marcado con **°** |

**Un nombre de barrio usado para nombrar una zona gastronómica que no coincide con el barrio es
uso corriente, no normativo.** Que «Palermo» esté en la ley de barrios no convierte al polo
gastronómico de Palermo en una figura normativa.

---

## Las 41

### Referencias publicadas

| id | nombre en la ficha | nivel | en qué se apoya |
|---|---|:--:|---|
| R01 | Palermo | **3** | uso corriente. Sus subzonas están en nivel 3 en `POLOS_NOMBRADOS.csv` (P091 Soho, P078 Hollywood, P073 Botánico) |
| R02 | Avenida Corrientes | **3** | uso corriente. P113 «Av. Corrientes · tramo teatral», nivel 3 |
| R03 | San Telmo | **3** | uso corriente. P103 «San Telmo», nivel 3. Existe el APH1 San Telmo–Monserrat, que protege pero no nombra al polo |
| R04 | Puerto Madero | **3** | uso corriente. P030 «Puerto Madero · diques 2 y 3» está en nivel 2, pero nombra una subzona, no la referencia |
| R05 | Belgrano | **3** | uso corriente. Su enclave, el Barrio Chino, es P072-6 en nivel 2 |
| R06 | Recoleta | **3** | uso corriente. P098 «Recoleta · Plaza Francia», nivel 3 |
| R07 | Costanera Norte | **3** | uso corriente consolidado y sostenido por señalética y prensa |
| R08 | Villa Crespo | **3** | uso corriente |
| R09 | Chacarita | **2** | **oficial de facto.** P068 se llama literalmente «Polo gastronómico Chacarita» y está en nivel 2 |
| R10 | Caballito | **3** | uso corriente |
| R11 | Boulevard Caseros | **3** | uso corriente. P102 «Bulevar Caseros», nivel 3, con la nota de que Turismo BA lo reconoce en su guía de Barracas |
| R12 | Centro y Microcentro | **3** | uso corriente. P116 «Microcentro», nivel 3. **Propongo sacar «segmentado» del nombre publicado:** es una descripción morfológica, no parte del nombre |
| R13 | Abasto | **2** | **oficial de facto.** P093 «Abasto» y P082 están los dos en nivel 2 |
| R14 | Avenida Boedo | **3** | uso corriente. P062 «San Juan y Boedo» está en nivel 2 pero nombra la esquina, no el corredor |
| R15 | Devoto | **3** | uso corriente. P016 «Plaza Arenales (Devoto gastronómico)», nivel 3 |
| R16 | Donado–Holmberg | **3** | uso corriente. P045 y P039 son «DoHo (Donado-Holmberg)», los dos en nivel 3 |
| R17 | Villa Urquiza | **3** | uso corriente |
| R19 | Federico Lacroze | **4 °** | **de trabajo.** Es el nombre de la avenida que mide el polígono, y los cinco grupos de prensa que abren su vía de reconocimiento hablan de **Fraga y Dorrego**. Nadie llama «Federico Lacroze» a ese polo |
| R20 | García del Río | **3** | uso corriente. Tres reporteos de La Nación en 2021, 2025 y 2026 lo nombran «el boulevard de García del Río» |
| R21 | La Paternal | **3** | uso corriente. P043 es «La Isla (La Paternal)», nivel 3 — «La Isla» nombra su núcleo |
| R22 | Villa Pueyrredón | **4 °** | **de trabajo.** Cero evidencia externa de cualquier tipo: nadie nombra este polo. El nombre es barrio más avenida |

### Zonas que se incorporan

| id | nombre en la ficha | nivel | en qué se apoya |
|---|---|:--:|---|
| Z23 | Flores · casco histórico | **3** | uso corriente |
| Z24 | Flores · Avellaneda y Pasaje Ruperto Godoy | **4 °** | descriptivo, barrio más ejes |
| Z25 | Floresta | **3** | uso corriente como barrio; los cuatro P de Floresta están en nivel 4 porque nombran esquinas |
| Z27 | Villa Santa Rita | **4 °** | no se encontró denominación para el polo |
| Z28 | Monte Castro | **4 °** | P025-2 «Monte Castro · Av. Lope de Vega», nivel 4 |
| Z31 | Villa Luro | **4 °** | no se encontró denominación para el polo |
| Z32 | Liniers · Mercado Andino | **2** | **oficial de facto**, y **con una decisión abierta al lado**: el nombre del enclave de Liniers está explícitamente sin resolver —sobran cinco candidatos— y es de Diego |
| Z33 | Mataderos | **3** | uso corriente. **Si el polo se nombrara por la Feria**, P006 «Feria de Mataderos y Casco Histórico» está en nivel 2 y la ficha subiría |
| Z35 | Balvanera · Once | **3** | «Once» es uso corriente fortísimo; los tres P de Balvanera están en nivel 4 porque nombran esquinas |
| Z37 | Almagro | **3** | uso corriente. Los tres P de Almagro están en nivel 4 |
| Z39 | Parque Avellaneda | **4 °** | no se encontró denominación para el polo |
| Z39b | Baek-ku · Barrio Coreano | **3** | uso corriente **dentro de la comunidad**, que es el uso que corresponde para un enclave. Comparable a P072-6 «Barrio Chino», nivel 2 |
| Z40 | Nueva Pompeya y Parque Patricios | **4 °** | dos barrios unidos por conveniencia. **Y hay una alternativa que sube el nivel:** si el polo se recortara a Parque Patricios, P027 «Distrito Tecnológico» está en **nivel 1** por Ley 2972/2008 |
| Z41 | Núñez | **3** | uso corriente. P067 «Bajo Núñez», nivel 3 |
| Z42 | Coghlan | **4 °** | ningún P de nombre parecido en los 124 |
| Z43 | Colegiales | **3** | uso corriente. Los tres P de Colegiales están en nivel 4 porque nombran esquinas |
| Z44 | Villa Ortúzar | **4 °** | no se encontró denominación para el polo |
| Z46 | Retiro | **3** | uso corriente. Los dos P de Retiro están en nivel 4 |
| Z47 | Monserrat y Congreso | **3** | uso corriente. P101+P099 «Congreso», nivel 3. **Propongo «y» en vez de «+»**, que es notación de trabajo |
| Z48 | San Cristóbal | **4 °** | los dos P de San Cristóbal están en nivel 4 |

---

## El reparto, y qué dice

| nivel | cuántas | |
|---|---:|---|
| 1 · normativo | **0** | |
| 2 · oficial de facto | **3** | Chacarita, Abasto, Liniers |
| 3 · uso corriente | **27** | |
| 4 · de trabajo · ° | **11** | |

**Ninguna de las 41 tiene nombre normativo, y es un resultado, no un hueco.** Las figuras
normativas de la Ciudad —los distritos creados por ley, con perímetro— **no nombran polos
gastronómicos**: nombran distritos productivos, culturales o audiovisuales que a veces contienen
uno. El único caso donde la ley podría dar el nombre es Parque Patricios, y sólo si el polo se
recortara al perímetro del Distrito Tecnológico.

**Y once de las 41 no tienen nombre propio.** Es la misma proporción que en las 124, donde son 74
de 124. Que una cuarta parte de las referencias admitidas del atlas no tenga denominación de uso
corriente **es la medida de cuánto del territorio gastronómico porteño nunca fue nombrado** — y,
para un programa que se propone construir identidad por zona, es el mapa del trabajo que tiene por
delante.

---

## Los cuatro casos que conviene que mires primero

**R19 · Federico Lacroze.** Lo bajé a nivel 4 porque el nombre no describe al polo: la geometría
mide la avenida y los cinco grupos de prensa hablan de Fraga y Dorrego. **Si la ampliación
decidida se mide y el perímetro nuevo cubre Fraga, el nombre debería cambiar, no el nivel.**

**Z32 · Liniers.** Es la única fila donde el nombre está formalmente abierto: hay cinco candidatos
y la decisión es tuya. La puse en 2 porque el Mercado Andino es una denominación oficial de facto,
pero el nombre de la referencia entera está sin firmar.

**Z40 · Nueva Pompeya y Parque Patricios.** Es la única fila que puede subir a nivel 1, y depende
de una decisión de recorte, no de nombre.

**R12 · Centro y Microcentro.** Le saqué «segmentado». Es la morfología de la referencia —área
segmentada— y no parte de su nombre; que aparezca en el nombre confunde el objeto con su forma.
