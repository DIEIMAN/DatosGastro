# Diagnóstico editorial por macrozona (Etapa V2-3)

**Fecha:** 2026-07-08 · **Carácter:** interpretación experimental, no técnica. Basado en la
inspección visual de los 8 tableros de
`outputs/polos_gastro/experimentos/pipeline_microzonas_v1/validacion/tableros/`. No se
modifica nada del pipeline: es lectura crítica de lo que ya está corrido.

Para cada caso: ¿único núcleo o varios?, ¿sobre-fragmentó?, ¿fusionó zonas distintas?,
¿límites razonables?, ¿hay corredores?, ¿sectores mal representados?

## Palermo

**Varios núcleos, y coinciden razonablemente con las subzonas editoriales.** 8 clusters:
C2 (244) cae casi entero sobre la elipse "Palermo Hollywood"; C5 (242) se solapa con
"Palermo Soho" pero se extiende bastante al sur y oeste de la elipse editorial — el núcleo
real parece más grande que el área editorial dibujada, no al revés; C0+C1 (Las Cañitas)
separan correctamente Las Cañitas en dos sub-núcleos contiguos (podría ser un único núcleo
partido de más, o dos realmente distintos — solo un conocedor de la zona lo dirime); C3
coincide con Palermo Chico; C7 con Palermo Nuevo/Botánico; **C6 es un corredor angosto
(72 locales) ubicado entre el centro geográfico de Palermo y Palermo Chico**, sin nombre
editorial propio — candidato a "zona emergente no mapeada" o a eje de conexión real.
**No fusiona zonas distintas** (no hay un cluster que abarque Soho+Hollywood a la vez).
**Límites razonables** en 6 de 8 clusters; C2 y C5 son los dos candidatos a segunda pasada
(> 240 locales cada uno, > 70 ha) — probablemente **sí mezclan más de un núcleo interno**
(p. ej. Soho puede tener 2-3 corazones distintos que el ojo entrenado reconocería).

## Avenida Corrientes

**Corredor + microcentro, con un desajuste editorial que vale la pena marcar.** El cluster
C5 (128 locales) es un corredor claro y angosto (norte-sur) — casi seguro el tramo real de
Av. Corrientes. Sin embargo, **la elipse editorial "Corrientes 9 de Julio-Callao" (el eje
oficial) queda vacía de clusters**, y el cluster más grande (C7, 133 locales, marcado
sobredimensionado) se ubica en San Nicolás/Microcentro, al este, fuera de esa elipse. Dos
lecturas posibles: (a) el contenedor de macrozona es demasiado ancho y absorbió San Nicolás
como si fuera "Corrientes" (el riesgo ya señalado del hull de semilla + buffer 500 m), o
(b) la concentración real de oferta gastronómica en esa macrozona editorial está más al
este de lo que el eje oficial supone. **No se puede resolver sin revisión humana de
terreno.** El resto (C0, C1, C2, C4, C6, C8) son núcleos chicos y razonables, sin fusión
aparente entre sí.

## San Telmo

**Multi-núcleo, con un caso claro de fuga fuera de zona.** C9/C8/C6/C7/C3/C5 forman un
racimo compacto y coherente alrededor del Mercado de San Telmo y el casco histórico —
coincide bien con "Entorno Mercado" y "Área Gastronómica". **C4 (32 locales) es un cluster
grande y separado, ubicado claramente al norte, fuera de toda elipse editorial de San
Telmo** (más cerca de Constitución/Av. San Juan): un conocedor de la zona probablemente
diría que no es San Telmo. **C1 (14 locales), al sur, también queda fuera de las elipses**,
territorio más cercano a Barracas. Sin fusión de núcleos distintos; sí dos casos de
**sector mal representado por el contenedor** (que es demasiado alto/bajo respecto del
polígono editorial real).

## Belgrano

**Un núcleo dominante que probablemente mezcla tres identidades editoriales distintas.**
C2 (88 locales, marcado sobredimensionado) se extiende sobre las tres elipses editoriales
a la vez: Barrio Chino, Cabildo/Juramento y Bajo Belgrano. Esto **no es necesariamente un
error del algoritmo** — puede ser que la oferta gastronómica real sea continua a lo largo
de esas manzanas — pero desde una lectura editorial, "Barrio Chino" es una identidad
gastronómica reconocible y distinta del resto, y perderla dentro de un cluster genérico
es una pérdida de información útil. **Candidato principal a segunda pasada.** C3 (14,
"Barrio Chino" literal) y C0 (16, cerca de Cabildo/Juramento) sí separan bien esas
identidades en paralelo — conviven un cluster grande y genérico con clusters chicos y
específicos, lo cual sugiere que la segunda pasada puede recuperar la distinción perdida.

## Chacarita

**El problema de la Tanda 2 (hull de 1.546 ha) está resuelto.** 7 clusters razonablemente
compactos y separados, sin fusión visible de zonas distintas. **C0 (34 locales) es un
corredor limpio y bien formado** (probablemente Av. Álvarez Thomas o Jorge Newbery), el
mejor ejemplo de corredor de los 8 casos. El resto son núcleos chicos-medianos dispersos
por la grilla, ninguno anormalmente grande. Sin capa editorial de referencia para
contrastar (Chacarita no tiene subzonas en fase16), pero la forma general es creíble para
alguien que conozca la zona: no hay indicios de sobre-fragmentación ni de fusión indebida.

## Villa Crespo

**Caso neutro, resultado razonable sin sobresaltos.** 9 clusters bien separados
espacialmente, ninguno cruza a otro visualmente, ninguno califica como sobredimensionado.
C6 (46 locales) tiene una forma alargada notoria (no fue marcado como corredor por el
umbral automático: revisar si el umbral de elongación/largo es demasiado estricto) que un
ojo humano probablemente leería como corredor también. Sin capa editorial para contrastar.
Sin evidencia de fusión de zonas distintas ni de fragmentación excesiva.

## Avenida Caseros / Barracas

**Resultado honesto pero de baja confianza, como se esperaba.** Solo 63 entidades y un
contenedor degradado (quedó con 1 punto semilla tras depurar apartados: el "hull" real es
casi un punto). Los 3 clusters (C0, C1, C2) están razonablemente separados y con nombres de
locales conocidos (Bar El Molino, La Perla, El Huracán), pero **el contenedor mismo no
representa de forma confiable el polo editorial "Caseros/Barracas"** — es la macrozona más
urgente para digitalizar a mano en vez de derivar de la semilla.

## Costanera Norte

**Fallo total y correcto: el pipeline dice "no sé" en vez de inventar.** Solo 2 entidades
del universo V1 caen dentro del contenedor construido; HDBSCAN (via el fallback DBSCAN)
no encuentra estructura; 100 % ruido. Esto **no es un defecto del algoritmo**: la
combinación semilla escasa (6 puntos, de los cuales 1 fue depurado por apartado) +
universo F01/F02 con poca cobertura en esa franja produce, correctamente, "sin evidencia
suficiente". Confirma que el gate de mínimo de puntos (Etapa 3) hace su trabajo: es
preferible este resultado vacío a un cluster forzado sobre 2 puntos.

## Síntesis de la Etapa V2-3

| Patrón | Casos donde aparece |
|---|---|
| Coincide bien con subzona editorial | Palermo (6/8 clusters), San Telmo (núcleo central), Belgrano (satélites) |
| Corredor limpio y creíble | Chacarita C0, Avenida Corrientes C5 |
| Núcleo dominante que probablemente mezcla identidades | Palermo C2 y C5, Belgrano C2, Avenida Corrientes C7 |
| Cluster fuera de la zona editorial esperada (contenedor demasiado amplio) | San Telmo C4 y C1, posiblemente Avenida Corrientes C7 |
| Corredor visible no detectado por el umbral automático | Villa Crespo C6 (a revisar el umbral) |
| Evidencia insuficiente, resultado vacío honesto | Costanera Norte |
| Baja confianza por contenedor degradado | Avenida Caseros / Barracas |

Ningún caso muestra el error más grave posible (fusión de dos macrozonas o subzonas
claramente distintas en un solo cluster irreconocible). El error dominante es el opuesto:
**núcleos que probablemente deberían dividirse** (van a la Etapa V2-4) y **contenedores que
se extienden más allá de la zona editorial real** (un problema de digitalización de
contornos, no de clustering).
