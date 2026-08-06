# CAMBIOS · de la V2.1 a las dos ediciones

**Entregables:**
`ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS.pdf` — edición de conducción · **51 páginas A4**
`ATLAS_TECNICO_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS.pdf` — edición técnica · 58 páginas A4
**Paquete:** `PAQUETE_ATLAS_EDICIONES_REVISION.zip` · **Fecha:** 2026-08-04

**Base:** `ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_V2_1.pdf`, que queda en esta carpeta
sin modificar, igual que la V2 y sus dos paquetes de revisión.

> **Lo que sigue documenta la derivación de la V2.1 a las dos ediciones (2026-08-03) y se
> conserva como registro.** La corrida posterior de maquetación y subzonas está al final,
> en «Corrida de prolijidad y de subzonas · 2026-08-04»: ahí la conducción pasa de 49 a 51
> páginas y de 28 a 31 controles, así que los totales de esta primera parte quedan
> superados por los de la última.

La edición de conducción se derivó **restando**. Ninguna cifra cambió, ninguna geometría
cambió, ninguna decisión territorial se reabrió. El control `diff_cifras_v21_conduccion`
compara las cifras publicadas de las 22 fichas y de los 29 bloques de mapa contra la V2.1:
**51 comparaciones, 51 PASS**.

La edición técnica es la V2.1 tal cual. El diff de texto contra la V2.1, página por página,
da **56 de 58 páginas idénticas y cero supresiones**: las dos únicas diferencias son las dos
adiciones declaradas —la portada dice que es la edición técnica y el Anexo G remite a la
edición de conducción—.

---

## Qué quedó hecho

1. **B1 · El vocabulario de método desapareció de la edición de conducción.** Las 21 familias
   de términos del encargo más ocho expresiones de jerga disfrazada de castellano —incluida
   "vista de detalle", que era el nombre de una sección entera— **no aparecen ni una vez** en
   las 49 páginas. El control `vocabulario_conduccion` recorre el texto extraído del PDF y
   hace fallar la producción ante cualquier aparición. La lista vive en un solo lugar del
   código, `scripts/lenguaje_conduccion.py`, y no se repite en ningún otro archivo.

   Las traducciones obligatorias se usaron con el registro pedido: "Se identificaron al menos
   211 locales… 204 estaban abiertos y 7 cerrados de forma temporaria", "646 locales
   relevados, contando una sola vez los que aparecían repetidos", "No se hizo un conteo propio
   de esta zona", "Es un mínimo: puede haber más, no menos". Las capas administrativas y las
   saturaciones con su denominador se eliminaron, como estaba indicado.

2. **B2 · El badge de cifra es una frase.** Desaparecieron el símbolo (`=`, `≥`, `◷`), la
   etiqueta en mayúsculas y la caja de color. Queda una línea destacada tipográficamente:
   *40 locales relevados* · *Al menos 211 locales* · *697 locales según un relevamiento
   anterior* · *Zona caracterizada, sin conteo propio*. Los cuatro casos se siguen
   distinguiendo; la distinción la lleva la frase.

3. **B3 · La ficha se reordenó según el lector.** Los cuatro títulos del proceso de trabajo
   —Lectura · Evidencia y método · Componentes y relaciones · Qué no se puede concluir— pasan
   a: **Qué es esta zona · Cuánta oferta hay · De qué se compone · Qué hay que tener en
   cuenta**. El primer bloque dice en positivo cómo es el lugar: la ficha de R01, que dedicaba
   once viñetas a lo que no se puede concluir sobre Palermo y ninguna a cómo es Palermo, ahora
   abre describiendo la zona y cierra con tres salvedades. Ninguna ficha supera las tres
   líneas del cuarto bloque.

   La duplicación se eliminó: "Qué no se puede concluir" arriba y "Advertencia común" al pie
   decían lo mismo en las 22 fichas. Queda **una sola advertencia, al pie de cada página**.

4. **B4 · La fuente y la fecha salieron de las 22 fichas.** Aparecen **una vez en todo el
   documento**, al pie del resumen ejecutivo, y en lenguaje llano: "Fuente: relevamiento
   propio de la Dirección General de Desarrollo Gastronómico. Los datos corresponden a julio
   de 2026."

5. **B5 · De siete anexos queda uno.** Sobrevive el Anexo A como tabla de consulta rápida, en
   dos páginas, con los encabezados reescritos: *Ref. · Zona · Qué tipo de zona es · Qué mide
   la cifra · Cuánta oferta hay*. Los valores de la columna de naturaleza también están en
   castellano: conteo propio, mínimo relevado, relevamiento anterior, sin conteo propio.

   Los anexos B, C, D, E, F y G se fueron completos a la edición técnica. En su lugar hay una
   página nueva, **"Cómo se hizo este Atlas y qué no dice"**, de seis párrafos, que cierra
   remitiendo a la edición técnica para el detalle metodológico.

6. **B6 · La página de lectura pasó de ocho cajas a tres.** Qué es una zona de este Atlas · por
   qué los números de distintas zonas no se comparan entre sí · qué son las áreas de los
   mapas. Una caja cada una, más una línea de cierre.

7. **B7 · El documento bajó de 58 a 49 páginas y se lo dejó bajar.** Al sacar el aparato
   metodológico, las ocho fichas que ocupaban una página entera dejaron de necesitarla: las 22
   entran de a dos por página, en 11 páginas contra las 15 de la V2.1. El plan se reorganizó
   en consecuencia y ahora cada ficha va seguida de su mapa y de su ampliación cuando la
   tiene, sin ir y volver. Los anexos pasan de 8 páginas a 3.

   Sobre el espacio vacío: se midió página por página la distancia entre el último elemento y
   la línea del pie. **Ninguna de las 49 páginas supera el cuarto de alto libre, salvo la 49**,
   que es el cierre en media carilla que pide el punto B5 del encargo y que se declara acá como
   excepción deliberada. En el camino se rehicieron el resumen ejecutivo, el índice —de tres
   columnas cortas a dos parejas, con el encabezado de sección repetido cuando una sección
   continúa—, la página de lectura y las dos tablas del Anexo A, que ocupaban un tercio de la
   hoja.

8. **B8 · Los dos controles nuevos, y los 26 anteriores.** La edición de conducción corre **28
   controles, los 28 en PASS**; la técnica corre los **26 de la V2.1, los 26 en PASS**.
   - `vocabulario_conduccion` — 29 términos vigilados, 0 apariciones en 49 páginas.
   - `diff_cifras_v21_conduccion` — 51 comparaciones, 51 PASS. Vigila las cifras publicadas,
     no los números de navegación (páginas del índice, "IR AL MAPA · p. N", pie de página),
     que cambian por definición al cambiar el plan de páginas.

   La inspección visual se rehízo para el nuevo total: `qa/QA_VISUAL_INSPECCION_49_CONDUCCION.csv`,
   **49 de 49 filas con hallazgo real**, cero PENDIENTE, 39 páginas OK y 10 con observación
   declarada.

9. **Un rótulo de mapa dejó de nombrar un objeto interno.** "Red occidental de calles
   documentadas", que el encargo señala como jerga disfrazada, se dibuja en la edición de
   conducción como **"Sector oeste de La Paternal"**. Es un cambio de rótulo: la geometría, la
   cifra y la lectura de R21 son las mismas. En la edición técnica el rótulo original queda
   intacto.

10. **La leyenda y el pie de los mapas hablan el mismo idioma que el resto.** "área de la
    referencia" → "área de la zona"; "componente interno" → "parte interna"; la nota del trazo
    punteado dejó de decir "no envolvente de oferta observada" y dice "no el contorno de la
    oferta encontrada". La sección "Vistas de detalle" pasó a llamarse **"Mapas ampliados"** y
    cada página se titula "MÁS DE CERCA".

---

## Qué quedó a medias

1. **Los rótulos de calle se cruzan con los rótulos de área en cinco mapas** (páginas 6, 10,
   16, 23, 40 y 43 de la edición de conducción). Es la misma cartografía de la V2.1 y las
   mismas láminas: en la edición técnica el cruce aparece en las páginas 6, 11, 18, 25, 43 y
   45. Esta fase no toca geometrías ni mapas, así que se declara y no se corrige.

2. ~~**La ampliación de Las Cañitas sigue mostrando las otras piezas de Palermo en el
   encuadre.** Aporta zoom y rótulo, no una capa de información nueva. Igual que en la
   V2.1.~~ **RESUELTO en la corrida del 2026-08-04 (S-02).** La causa no era el encuadre: la
   capa de componentes no tenía ninguna entrada para R01, así que el zoom caía sobre la
   envolvente entera. Ver el bloque 2 al final de este documento.

3. **Las ampliaciones de R12 y R15 siguen pareciéndose a su mapa principal.** En R15 el corpus
   no cerró geometría del núcleo, así que la vista repite el polo completo: BLOQUEADO-03 sigue
   abierto por decisión.

4. **La página 49 deja más de un cuarto de alto libre.** El encargo pide media carilla para el
   cierre y el encargo pide que ninguna página pase el cuarto vacío. Se respetó lo primero,
   porque es la instrucción específica de esa página, y se declara acá el apartamiento de lo
   segundo.

---

## Qué directamente no se hizo, y por qué

1. **No se reescribió ninguna frase que no pudiera decirse en castellano sin perder su
   contenido.** El encargo pide anotar esos casos en vez de suavizarlos. No apareció ninguno:
   las 22 fichas se pudieron reescribir enteras conservando cada salvedad que entra en el
   documento. Lo que no entró no se suavizó: se eliminó del documento y viajó completo a la
   edición técnica, que es exactamente lo que el encargo previó.

2. **Dos afirmaciones se retiraron por no tener respaldo en la ficha de la V2.1**, y el control
   de cifras fue quien las encontró:
   - en R15, la conducción decía que el núcleo de Plaza Arenales está en Villa Devoto,
     **Comuna 11**. La comuna está en el registro de decisiones del proyecto, no en la ficha
     publicada de R15. Quedó "en Villa Devoto", sin el número;
   - en el bloque del mapa de R22, la conducción agregaba el estado de los locales
     (**152 abiertos y 6 cerrados**). Esos números están en la ficha de R22, pero el bloque del
     mapa de la V2.1 no los publicaba. El bloque volvió a decir lo que decía.

3. **No se cambió el nombre institucional de ninguna zona.** "Centro/Microcentro segmentado"
   sigue llamándose así, aunque el nombre sea más técnico que el resto del documento: es la
   denominación del corpus y renombrarla excedía el encargo.

4. **La etiqueta fina de tipología no está en la edición de conducción.** Expresiones como
   "Polo documentado sin unidad espacial estabilizada" o "Lectura multinodo con componentes
   independientes" no son términos prohibidos, pero son jerga para el destinatario. En la
   ficha y en el Anexo A se usa la familia territorial —Polo, Polo con subzonas o partes, Eje
   o corredor, Área segmentada, Referencia dispersa—, que es la misma que da el color en el
   mapa. Las 22 etiquetas finas siguen enteras en la edición técnica.

5. **La cartografía no se redibujó.** Los mapas de las dos ediciones salen de las mismas capas
   y del mismo código. Lo único que difiere es el alto disponible para el dibujo, porque el
   bloque de tres líneas del pie tiene otra longitud al estar escrito en castellano llano; la
   escala rotulada y las formas son las mismas.

---

## Reproducción

Desde la raíz del repositorio, sin red:

```
.venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_geometrias_editoriales_v2.py
.venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_atlas_v2.py --finalize-visual
```

El segundo produce **las dos ediciones** y un único paquete de revisión. Con
`--edicion conduccion` o `--edicion tecnica` se produce una sola. El generador verifica los
seis insumos canónicos por SHA-256, trabaja sin red, rechaza referencias distintas de R01-R22,
rechaza un total de páginas distinto del declarado por cada edición y no modifica ningún
activo fuente.

## Dónde mirar

| Qué | Archivo |
|---|---|
| Verificación frase por frase, V2.1 contra conducción | `qa/TRAZABILIDAD_LENGUAJE.csv` (88 filas, 22 zonas × 4 bloques) |
| Ninguna cifra se movió | `qa/DIFF_CIFRAS_V21_CONDUCCION.csv` |
| Ningún término de método llegó al lector | `qa/QA_VOCABULARIO_CONDUCCION.csv` |
| Los 28 controles de la conducción | `qa/QA_AUTOMATICO_CONDUCCION.csv` |
| Los 26 controles de la técnica | `qa/QA_AUTOMATICO_TECNICA.csv` |
| Inspección visual de las 49 páginas | `qa/QA_VISUAL_INSPECCION_49_CONDUCCION.csv` |
| Plan de páginas de la conducción, con su equivalente técnico | `matrices/PLAN_PAGINAS_ATLAS_CONDUCCION_EFECTIVO_49.csv` |
| Los 29 bloques de mapa y de dónde sale cada línea | `qa/TRAZABILIDAD_TEXTOS_B3_CONDUCCION.csv` |

---

# Corrida de prolijidad y de subzonas · 2026-08-04

Dos bloques sobre la edición de conducción: uno de maquetación, uno de contenido
cartográfico. **Ninguna cifra cambió, ninguna envolvente cambió, ninguna decisión
territorial se reabrió.** El control `diff_cifras_v21_conduccion` sigue en 51 comparaciones
y 51 PASS, y `vocabulario_conduccion` en 0 apariciones sobre las 51 páginas.

La conducción pasa de **49 a 51 páginas** por las dos ampliaciones nuevas de Palermo (S-03).
La edición técnica sigue en 58 páginas: cambian tres de ellas, las tres por la misma
corrección de regresión cartográfica que pide el bloque 2.

## La causa común de M-07 y de dos controles vacíos

`build_atlas_v2.py` se ejecuta como `__main__`. El `import build_atlas_v2` de
`render_conduccion.py` cargaba una **segunda copia del módulo**, con sus variables globales
en el valor de importación. `configurar_edicion()` reconfiguraba la copia de `__main__` y
las páginas de conducción seguían leyendo la otra. De ahí salían:

- los veinte `Ir al mapa · p. N` con la numeración de 58 páginas (R22 remitía a la p. 50 en
  un documento de 49) —lo que reporta M-07—;
- `QA_AJUSTE_FICHAS_CONDUCCION.csv` vacío, con encabezado y ninguna fila, porque las 22
  mediciones se acumulaban en la lista de la copia que nadie leía;
- el control de texto cortado sin ver ni un solo texto de las páginas de conducción, y
  declarando «58 páginas revisadas» en una edición de 49.

Se corrige registrando el módulo en `sys.modules` antes de importar los adaptadores. Una
sola copia. `QA_AJUSTE_FICHAS_CONDUCCION.csv` tiene ahora sus 22 filas.

## Bloque 1 · Maquetación

**M-01 · Márgenes.** El margen de encuadernación alternado se reemplaza por 15 mm iguales a
izquierda y derecha en las **51 de 51 páginas** de la conducción: el bloque de texto queda
centrado en la hoja. La técnica conserva el margen de la V2.1.

**M-02 · Colisiones.** El defecto era de medición: el alto de un texto se cuenta desde su
línea de base hacia arriba, y el generador usaba la línea de base como si fuera el techo,
así que las mayúsculas subían por encima de la caja anterior. Se agrega `base_bajo()`, que
posiciona por el techo real, y el control **`cajas_sin_colision`**, que compara cada caja
dibujada contra el texto del PDF terminado. 51 páginas, 0 colisiones.

**M-03 · Ritmo vertical.** Una escala de cuatro valores —sección 26, bloque 16, párrafo 9,
línea 4— en `RITMO`. Todo espacio de la conducción sale de ahí. Los tres valores distintos
para la misma jerarquía del resumen desaparecieron.

**M-04 · Mayúsculas.** Queda **una sola capa**: el encabezado de sección que corre arriba de
cada página. Bajaron a capitalización normal los títulos de caja, los sufijos de página
(`· Mapa`, `· Más de cerca`), los enlaces (`Ir al mapa`, `Volver a la ficha`), los rótulos de
tabla de la p6 y las dos versalitas de la portada. Los distingue el peso y el color.

**M-05 · Cajas de la p4.** Se eliminó el inflado: cada caja se ajusta a su contenido. Lo que
antes rellenaba la caja ahora queda al pie de la página.

**M-06 · Anexo A.** El encabezado `Qué tipo de zona es` medía 102,9 pt en una columna de
99,2 y se montaba sobre el de al lado; se dibujaba sin medir. Ahora `draw_table` **corta la
producción** si un encabezado no entra en su columna. Y se eliminó la columna `Qué mide la
cifra`: repetía lo que ya dice `Cuánta oferta hay` —literalmente igual en cinco de once
filas—. Quedan cuatro columnas.

**M-07 · Enlaces.** Recalculados por la corrección de arriba. Control nuevo
**`enlaces_coherentes`**: para cada referencia textual `p. N` verifica que N sea la página
del destino y que el enlace clicable apunte al mismo lugar. **44 referencias, 44 PASS.**

**M-08 · Índice.** `Zonas R01-R22 (continúa)` lleva ahora a la página donde la sección
continúa, no al inicio de la sección.

## Bloque 2 · Subzonas de Palermo y Puerto Madero

**S-01 · Diagnóstico confirmado.** `componentes_editoriales_v2.geojson` no tenía ninguna
entrada para R01. La rama de la fuente fase24 del constructor de geometrías —la que produce
R01 a R04— era la única que nunca registraba componentes: usaba los tres polígonos nombrados
para componer la envolvente y descartaba los nombres. Se recuperan con el mismo mecanismo que
usan Belgrano y Chacarita. **La envolvente no cambia**: son las mismas piezas con las que ya
se componía, ahora con su nombre. Las tres se recortan contra la envolvente final para que el
rótulo caiga sobre la tinta que el mapa dibuja; suman 2,713 km², exactamente el área de la
envolvente. El mapa de Palermo rotula las tres subzonas.

> Precisión sobre el reporte: el mapa no rotulaba «Palermo» nueve veces. El halo de los
> rótulos se dibuja con ocho copias desplazadas más el texto real, así que la extracción de
> texto ve nueve veces cada rótulo del Atlas. Era **un** rótulo «Palermo» y ninguna de las
> tres partes: el problema de fondo es exactamente el que describe el encargo.

**S-02 · Las Cañitas.** Confirmado que no era un zoom: al no haber componentes de R01, el
encuadre caía sobre la envolvente entera con un margen casi igual al del mapa principal.
Ahora hay un método propio, `mapa_subzona()`: encuadre ajustado a la pieza con margen de
contexto, **escala propia de 250 m**, el resto de Palermo en gris punteado y las avenidas del
entorno rotuladas desde el callejero oficial GCBA.

**S-03 · Dos ampliaciones nuevas.** Palermo Soho y Palermo Hollywood, con el mismo
tratamiento, en las páginas 9 y 10. **Total nuevo: 51 páginas.** Son páginas de la conducción;
la técnica sigue con sus siete vistas de detalle.

**S-04 · Puerto Madero.** Hay que corregir la premisa: la ficha publicada **no nombra**
Docks, sector costero ni Dársena Sur, en ninguna de las dos ediciones, y el corpus
institucional declara `subunidades: []` para R04. Lo que sí existe, en la misma fuente
cartográfica que las tres partes de Palermo, son **dos polígonos nombrados** —Docks y Dársena
Sur— que son exactamente las dos piezas que el mapa ya dibujaba sin nombre. Se recuperan y se
rotulan, y la línea «Qué muestra este mapa» pasa a nombrarlas. **«Sector costero» no se
rotula: en la fuente es una línea, no un área**, y no se le inventa un polígono.

**S-05 · Control nuevo `mapas_rotulan_lo_que_prometen`.** Para cada mapa, si la línea «Qué
muestra este mapa» nombra partes internas, esas partes tienen que estar rotuladas. **31
mapas, 31 PASS**; seis nombran partes en su pie. Es el control que faltaba: habría hecho
fallar la producción de Palermo desde la V2.

## Un hallazgo de la revisión visual, fuera de la lista

El mapa de la Costanera Norte rotulaba sus cuatro piezas **«Componente 1» a «Componente 4»**,
que es la palabra interna del proyecto y no un nombre. Se cambia por «Tramo 1» a «Tramo 4»,
que es la palabra que usa la propia ficha («cuatro tramos separados sobre el frente
costero»). No se les inventa un nombre de lugar, que sería una decisión territorial. Es el
mismo tratamiento que ya tenía «Red occidental de calles documentadas» → «Sector oeste de La
Paternal». La edición técnica conserva el rótulo original.

## Lo que queda declarado

1. **Espacio libre al pie de las páginas 4, 5 y 51.** Es la consecuencia directa de ajustar
   las cajas a su contenido (M-05) y de no repartir el sobrante a ojo (M-03). El cuerpo de
   texto se agranda hasta 13,5 pt —por encima quedaría más grande que el título de la
   página— y lo que sobra queda abajo, donde se lee como margen. Se aparta de la regla de
   «ningún cuarto de alto libre» del encargo anterior; las dos instrucciones no se pueden
   cumplir a la vez y esta corrida elige la nueva.
2. **Los cruces de rótulo de calle con rótulo de área** siguen en las páginas 12, 18, 25, 42
   y 45. Es la misma cartografía de la V2.1 y esta corrida no toca geometrías.
3. **Las ampliaciones de R12 y R15** siguen pareciéndose a su mapa principal. BLOQUEADO-03
   sigue abierto por decisión, igual que BLOQUEADO-02 en R17.
4. **El índice agrupa por sección, no por orden de lectura**: «Mapas ampliados» arranca en la
   p. 9 y aparece después de entradas de la p. 46. Es la estructura del índice de la V2.1;
   cambiarla es una decisión editorial y queda para tu firma.
5. **`QA_VISUAL_INSPECCION_49_CONDUCCION.csv`** queda en la carpeta como registro de la
   edición anterior de 49 páginas. La inspección vigente es la de 51.

## Controles

| Edición | Controles | Resultado |
| --- | --- | --- |
| Conducción | 31 | 31 PASS |
| Técnica | 28 | 28 PASS |

Los tres nuevos son `enlaces_coherentes`, `cajas_sin_colision` (solo conducción) y
`mapas_rotulan_lo_que_prometen` (las dos ediciones).

## Verificación

- `qa/QA_ENLACES_COHERENTES_CONDUCCION.csv` — 44 referencias «p. N», 44 PASS.
- `qa/QA_MAPAS_PROMETIDOS_CONDUCCION.csv` — 31 mapas, qué promete el pie y qué rotula el mapa.
- `qa/QA_COLISIONES_CAJA_CONDUCCION.csv` — sin colisiones.
- `qa/QA_VISUAL_INSPECCION_51_CONDUCCION.csv` — 51 páginas, 42 OK y 9 con observación declarada.
- `qa/DIFF_CIFRAS_V21_CONDUCCION.csv` — 51 comparaciones, 51 PASS.
- Diff de texto de la técnica contra la entrega anterior: **55 de 58 páginas idénticas**. Las
  tres que cambian son el mapa de R01, la ampliación de Las Cañitas y el mapa de R04, por la
  corrección de la regresión cartográfica.
