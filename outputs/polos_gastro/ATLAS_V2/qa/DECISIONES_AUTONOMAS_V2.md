# Decisiones autónomas — Atlas V2

Registro llevado **a medida que avanza la ejecución**, no al final.

Se anota aquí toda decisión que cambia lo que el mapa o el texto **afirma sobre el
territorio**. Las decisiones de implementación (nombres de funciones, tolerancias de
render, estructura de archivos) no se registran.

Convención: **BLOQUEADO** = no se puede resolver sin inventar datos; se deja como está.

---

## D-A-01 · R02 Avenida Corrientes: exención de recorte contra R12

**Qué se presentó.** El recorte por línea media partía el corredor de Av. Corrientes en
tres tramos inconexos, porque los nodos declarados del Centro (R12/C-S01 Florida×Corrientes,
C-S04 Av. de Mayo) reclaman el terreno que el corredor atraviesa.

**Opciones.** (a) Aceptar los tres tramos. (b) Exentar el par como co-localizado declarado.

**Qué elegí.** (b), por instrucción explícita T-1. R02 se dibuja **por encima**
del relleno de R12.

**Apoyo en el corpus.** Ninguna ficha declara que el corredor de Corrientes sea
discontinuo. El corpus sí registra la co-localización: `GA-R12-CS08-CONTROL` tiene
`referencia_id = "R12;R02"` y regla `eje_tramo_alturas ['CORRIENTES AV.'] h=800-2000
buffer=200.0`, con la observación "Cero consultas; no redelimita ni reabre R02" — es decir,
el corpus reconoce que la avenida atraviesa el Centro y mantiene ambos productos separados
sin declararlos mutuamente excluyentes.

**Qué se vería distinto.** Con (a), el lector vería el corredor cortado en tres y
concluiría que la oferta de Corrientes se interrumpe en el Microcentro — una discontinuidad
que nadie midió.

**Alcance de la exención.** Es por declaración del corpus, no por registro geométrico. Ver
D-A-02 para los otros ejes revisados bajo el mismo criterio.

---

## D-A-02 · R14, R19 y R20: revisión del mismo corte artificial

**Qué se presentó.** La conducción del proyecto pidió revisar si otros ejes sufren el corte
que motivó D-A-01.

**Qué encontré, caso por caso.**

- **R14 Avenida Boedo** — sin solape con ninguna referencia. No hay corte. Nada que decidir.
- **R20 García del Río** — sin solape con ninguna referencia. No hay corte. Nada que decidir.
- **R19 Federico Lacroze** — solapa con R09 Chacarita (154.932 m²) y con R01 Palermo
  (31.672 m²). **El recorte se mantiene en ambos casos.**

**Apoyo en el corpus para mantener el recorte de R19.** La ficha de R09 dice, textual:
"Lacroze es control; sin Chacalermo ni fusión con R19, Palermo o Villa Crespo". Es una
declaración explícita de no fusión, exactamente el caso que la regla general de T-1
excluye de la exención. Para R01/R19 no hay declaración de co-localización que habilite
exentar, y R01 declara "Identidad propia; no absorber R08 ni R09".

**Qué se vería distinto.** Exentando R19 se vería el corredor de Lacroze superpuesto a
Chacarita, que es precisamente la lectura "Chacalermo" que el corpus prohíbe por escrito.

---

## D-A-03 · R09 y R10: envolvente por subunidad declarada

**Qué se presentó.** Al derivar de todos los puntos de la zona, el buffer fusionaba los
focos que el corpus declara independientes: R09 "Focos independientes Newbery y Dorrego",
R10 "Componentes independientes en narrativa multinodo".

**Qué elegí.** Envolver por subunidad declarada, por instrucción T-2, sin bajar
el buffer.

- R09 → `Z02-S1 Corredor Newbery` y `Z02-S2 Núcleo Dorrego` (ambos `SUBUNIDAD_ANALITICA`).
- R10 → `Z03-S1 Pedro Goyena` y `Z03-S2 Primera Junta–Mercado del Progreso`.

**Exclusiones y su fundamento.**
- `Z03-S4 Parque Rivadavia`: la ficha de R10 dice "Z03-S4 fue retirado y no forma parte de
  la lectura vigente". Queda fuera.
- `Z03-S3 Patio de los Lecheros`: estado `CONTROL_NO_ADOPTABLE`, rol
  `CONTROL_PUNTUAL_REPRODUCIBLE`. Es control, no producto. Queda fuera.
- `CONTROL_VECINO` y `AREA_TRANSICION` de Z02: controles, quedan fuera.

**Consecuencia declarada.** El área dibujada ya no cubre la totalidad de los registros que
la cifra cuenta. Esto **no se disimula**: la línea "Qué mide la cifra" del bloque B3 lo dice
explícitamente en cada ficha afectada. No se agrega nube de puntos para los registros que
quedan fuera del área.

**Qué se vería distinto.** Con la envolvente única, el lector vería un polo compacto donde
el corpus documentó núcleos separados.

---

## D-A-04 · R05 Belgrano: agrupamiento por centralidad

**Qué se presentó.** R05 se dibujaba como seis manchas sueltas, ilegibles a escala de
ciudad, mientras su ficha habla de "3 centralidades".

**Qué encontré.** La capa cerrada `BELGRANO_PRESENTACION_V3_1.geojson` **sí trae el
atributo**: tres registros con `nombre_publico` y `categoria_publica`:

| nombre_publico | categoria_publica | piezas |
|---|---|---|
| Barrio Chino–Belgrano C | CENTRALIDAD_PRINCIPAL | 4 |
| Cabildo–Juramento | EJE_INTERNO | 2 |
| Belgrano R | SECTOR_SECUNDARIO | 1 |

**Qué elegí.** El caso (a) de la instrucción T-3: agrupar las siete piezas en **tres multiparte por
centralidad**, mismo color y un solo rótulo por grupo. No se subió el cierre morfológico:
la geometría no se toca, solo se agrupa y se rotula.

**Precisión sobre los nombres.** La instrucción T-3 mencionaba "Bajo Belgrano" como tercera
centralidad;
en la capa cerrada "Bajo Belgrano" no es un registro propio sino una
`referencia_secundaria` dentro de Barrio Chino–Belgrano C. Los tres grupos que existen son
los de la tabla. Se rotulan esos, no otros.

**Qué se vería distinto.** Sin agrupar, el lector contaría seis referencias donde el corpus
declara tres centralidades.

---

## D-A-05 · R04 Puerto Madero: recorte parcial contra tierra

**Qué se presentó.** La envolvente de R04 incluía superficie de agua, lo que afirma que el
espejo de agua es polo gastronómico.

**Qué encontré.** **No existe capa de hidrografía en el repositorio.** Busqué en `data/raw/`,
`PolosGastro/cartografia/`, el callejero GCBA y todos los GeoJSON del subproyecto: no hay
capa de agua, diques ni línea de costa. El callejero es 100% `LineString` de vías. El
polígono oficial del barrio Puerto Madero (5,046 km²) **incluye los diques**.

**Qué hice.** Recorté R04 contra la unión de los polígonos barriales oficiales
(`data/raw/geo_barrios.geojson`), que elimina la superficie que caía sobre el Río de la
Plata, fuera de toda superficie barrial. Es sustracción de superficie donde con certeza no
hay locales, con fuente oficial, sin inventar nada. El recorte se aplica **solo a R04**;
ningún parque se recorta (Costanera Norte queda intacta).

**Corrección de esta entrada (V2.1, hallazgo R-01 de la auditoría externa).** La versión
anterior decía "envolvente 3,736 km² menos 0,807 km² recortados" y no cerraba contra el
R04 entregado. El error era omitir un paso: las dos cifras pertenecían a etapas distintas
de la cadena. La cadena completa, recomputada desde las fuentes, es:

| Paso | Área |
|---|---|
| Polígonos editoriales cerrados de origen | 4,642435 km² |
| Recortados contra tierra barrial oficial (se quitan 0,949302 km² de río) | 3,693133 km² |
| Envolvente editorial de ese núcleo (cierre 80 m + suavizado) | 3,693680 km² |
| **Tras el recorte mutuo por línea media contra R12** | **3,369573 km²** |

El paso faltante era el cuarto: 3,3696 km² es una cifra **posterior** al recorte mutuo, y se
la estaba restando de una envolvente **anterior** a él. Sin el recorte contra tierra, la
envolvente habría medido 4,076088 km², de los cuales 0,813771 km² caían fuera de todo
polígono barrial —de ahí el 0,807 aproximado que traía el registro—. La geometría entregada
siempre fue la correcta; el que se contradecía era este texto.

**Qué queda sin resolver.** Nada: los diques interiores se descontaron en V2.1. Ver
**D-A-10** y el cierre de BLOQUEADO-01.

---

## D-A-06 · R17 Villa Urquiza: no se pudo envolver por subunidad

Ver **BLOQUEADO-02**.

---

## D-A-10 · R04 Puerto Madero: los diques descontados (cierra BLOQUEADO-01)

**Estado: BLOQUEADO-01 CERRADO en V2.1.**

**Qué se presentó.** BLOQUEADO-01 quedó abierto en V2 porque no existía capa de
hidrografía en el repositorio y los proxies disponibles recortaban también plazas y parques.

**Qué apareció.** El paquete `INVESTIGACION_DESBLOQUEOS_V21` aportó una máscara de los
cuatro diques reconstruida desde OpenStreetMap vía Overpass (relaciones 2364286, 2364166,
2364163 y 2364162; ODbL 1.0; acceso 2026-08-03) y la contrastó contra la capa oficial
`cuerpos_de_agua_mapa_base_v2` del WMS de IDECABA: **97,113% de coincidencia raster**.

**Qué verificó la auditoría externa antes de habilitar la integración.** Que
`r04_original.geojson` mide 3,369573 km², idéntico al R04 del PDF V2 —es decir, que la
máscara se aplica sobre la geometría correcta y no sobre una variante—.

**Qué elegí.** Integrar **la diferencia, no la máscara completa**. Se resta únicamente la
intersección de la máscara con R04; la parte de la máscara que excede la envolvente no se
toca. La sustracción se aplica al final de la cadena, sobre la geometría ya recortada y
pulida, para que el resultado sea exactamente el que la auditoría verificó.

| Concepto | Área |
|---|---|
| R04 en V2 | 3,369573 km² |
| Máscara total de los cuatro diques | 0,403546 km² |
| Agua efectivamente sustraída (intersección) | 0,224161 km² |
| **R04 en V2.1** | **3,145412 km²** |

**Alcance y control.** El generador **falla** si la máscara toca cualquier referencia que
no sea R04: se verifica referencia por referencia en cada corrida. Ningún parque ni plaza
entra en la sustracción. Ninguna cifra, universo ni cota se modifica: R04 no tiene cifra
canónica comparable y su naturaleza declarada no depende del área.

**Qué cambia en la página.** La p15 muestra los cuatro diques como huecos del polígono, y
la línea "Qué no es" deja de decir que el área incluye los diques: ahora declara que los
excluye y con qué fuente.

**Fuente declarada.** OpenStreetMap/Overpass, ODbL 1.0, validada contra el WMS oficial de
IDECABA. Es cartografía pública de acceso abierto, no una geometría producida por nosotros.

**Confianza.** Media-alta. La fuente vectorial es comunitaria; el contraste con la capa
oficial es fuerte. La sustracción no redefine el perímetro terrestre de R04.

---

## BLOQUEADO-02 · Los tres ejes de R17 Villa Urquiza

**Qué falta.** Geometría de los ejes Monroe y Congreso.

**Qué hay.** La ficha de R17 dice "Triunvirato, Monroe y Congreso son componentes internos".
En el corpus solo existe **un** eje con geometría: `AREAS_TANDA2_ANALISIS_REPARADAS.geojson`,
zona Z10, trae `AREA_PRINCIPAL` (unión del barrio Villa Urquiza) y un único
`EJE_REFERENCIA` construido como `eje calles=['TRIUNVIRATO AV.'] barrios=['Villa Urquiza']`.
Monroe y Congreso no tienen geometría en ninguna capa cerrada.

**Por qué no lo resuelvo.** Construir los ejes faltantes desde el callejero replicando el
método documentado sería generar geometría que el corpus nunca produjo ni cerró. Usar los
clusters analíticos de `CLUSTERS_BASELINE_TANDA2_V1.geojson` sería publicar objetos
analíticos que el Atlas nunca publicó.

**Estado. BLOQUEADO-02 SIGUE ABIERTO, y esa es la respuesta correcta.** El paquete de
desbloqueos ofreció alternativas de trazado para Monroe y Congreso; la auditoría externa
verificó que incluyen entre 40 y 50 de los 189 puntos (Monroe) y entre 18 y 26 (Congreso).
Adoptar cualquiera convertiría una regla analítica en un eje institucional que el corpus
nunca cerró. **No se integran.**

**Qué sí se hizo en V2.1, sin decidir nada (D-02 de la auditoría).** Monroe y Congreso se
rotulan en el mapa de la p39 como **calles de referencia del callejero oficial GCBA**, en
gris de basemap, igual que las demás calles rotuladas del Atlas. No se dibujan como ejes de
producto, no llevan color de familia y no entran en ninguna envolvente. Con eso desaparece
la disonancia entre la ficha, que nombra tres ejes, y el mapa, que dibujaba uno.

R17 conserva su envolvente única de puntos observados, con el eje Triunvirato como
componente interno rotulado. La ficha mantiene la mención de los tres componentes; el mapa
ubica el único que tiene geometría cerrada, y la línea "Qué muestra este mapa" lo dice.

**Cómo se destraba.** Cerrando la geometría de Monroe y Congreso en el corpus territorial,
con el mismo método que Triunvirato.

---

## D-A-07 · Paleta C: la trama se mantiene también en el Camino B

**Qué se presentó.** Condición para fijar D-4: verificar que la trama de familia no
embarre la forma en las ocho referencias que ya llevan borde punteado.

**Qué hice.** Recorté R18 y R22 del mapa general del PDF, a tamaño real de página, a 4× y
en escala de grises (`qa/AG3_PALETA_C_TEST_CAMINO_B.png`).

**Qué elegí.** Mantener la trama en las ocho. En R22 el borde punteado y la trama conviven
sin confundirse, y ambos sobreviven al pasaje a gris. En R18 —un disco de unos 8 mm en
página— no se distingue ni la trama ni el punteado, pero tampoco se distinguiría ningún
otro recurso a ese tamaño: es un límite de escala, no un conflicto entre los dos indicios.

**Qué se vería distinto.** Quitando la trama al Camino B, esas ocho referencias perderían
su familia en la impresión en blanco y negro y quedarían identificadas solo por el número.

**Consecuencia declarada.** Por debajo de unos 10 mm en el mapa general (R18, R20 y el
tramo de R02), la identificación depende del número y de la tabla lateral, no del relleno.

---

## D-A-08 · R06 Recoleta: el badge no anuncia un antecedente que no existe

**Qué se presentó.** R06 declara `naturaleza = historica_metodologica` pero su cifra es
`SIN_CIFRA_CANONICA_COMPARABLE`. Con la clave visual del badge, la ficha mostraba
"ANTECEDENTE PREVIO" encabezando un valor que dice que no hay cifra.

**Opciones.** (a) Dejarlo como sale del canon. (b) Tratar la ausencia de cifra como tal en
la presentación, sin tocar el dato.

**Qué elegí.** (b). Cuando la cifra es `SIN_CIFRA_CANONICA_COMPARABLE`, la ficha usa la
línea secundaria en cuerpo normal, cualquiera sea la naturaleza declarada. **El campo
`naturaleza` no se modifica**: sigue viajando intacto al Anexo A, donde R06 figura como
antecedente histórico/metodológico sin cifra.

**Apoyo en el corpus.** La ficha de R06 dice "Sin cifra canónica comparable disponible para
publicación" y "no publicar núcleos analíticos".

**Qué se vería distinto.** Con (a), el lector leería "antecedente previo" como si hubiera un
número detrás.

---

## D-A-09 · Resumen ejecutivo: agrupar por método, no ordenar por tamaño

**Qué se presentó.** El resumen debía responder "cuáles concentran más oferta relevada" sin
construir el ranking general que el corpus prohíbe.

**Qué elegí.** Cuatro grupos, cada uno internamente comparable porque comparte método y
universo: relevamiento propio deduplicado; directorio comercial en línea deduplicado; pisos
censados; referencias sin conteo comparable. Dentro de cada grupo las cifras se listan de
mayor a menor. Entre grupos se dice explícitamente que no se comparan ni se suman.

**Apoyo en el corpus.** Los cuatro grupos no son una invención editorial: se corresponden con
`RESUMEN_UNIVERSOS_TANDA1_V4_4`, `RESUMEN_UNIVERSOS_TANDA2_V1` y las cotas de los Grupos A,
B y C, que ya están separados en el canon.

**Qué se vería distinto.** Una lista única de las 22 ordenada por número habría puesto a
Caballito (907, conteo cerrado) por encima del Centro (≥797, piso censado), sugiriendo una
diferencia que los métodos no permiten afirmar.

---

## BLOQUEADO-03 · Núcleo de Plaza Arenales en R15 Devoto

**Qué falta.** Geometría del núcleo estable de R15.

**Qué hay.** La ficha de R15 dice "núcleo estable en torno de Plaza Arenales y una periferia
contextual no estabilizada". En el corpus, la zona Z08 solo tiene `AREA_PRINCIPAL`
(unión del barrio Villa Devoto). No hay subunidad ni trazado del núcleo.

**Por qué no lo resuelvo.** Delimitar el núcleo a partir de la densidad de puntos sería
producir una geometría que el corpus no cerró, y la vista de detalle pasaría a afirmar un
límite que nadie decidió.

**Estado. BLOQUEADO-03 SIGUE ABIERTO, y esa es la respuesta correcta.** El paquete de
desbloqueos propuso un radio de 300 m alrededor del centroide de la plaza. **No se integra:**
un buffer sobre el centroide de una plaza no es un núcleo gastronómico, y con 25 de 119
puntos adentro es el mismo caso que el disco de R18, que el Atlas ya rotula como área de
consulta y no como núcleo.

**Lo que sí aporta el paquete y queda registrado (D-03 de la auditoría).** Con fuente
oficial —Espacios Verdes GCBA— se confirma que **Plaza Arenales está en Villa Devoto,
Comuna 11**. Eso valida la denominación "Devoto" que el Atlas ya venía usando para R15. Es
una confirmación de nomenclatura, no una geometría nueva: no cambia el mapa ni la cifra.

La vista de detalle de R15 (p. 36) amplía el polo completo y su primera línea dice que el
mapa no delimita el núcleo. Queda declarado como pendiente.

**Cómo se destraba.** Cerrando la subunidad del núcleo en el corpus territorial, con el
mismo método con que se cerraron Z02-S1, Z02-S2, Z03-S1 y Z03-S2.
