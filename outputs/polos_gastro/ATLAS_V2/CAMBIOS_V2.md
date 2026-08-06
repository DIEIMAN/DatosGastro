# CAMBIOS V2 → V2.1 — qué cambió, y qué no

**Entregable vigente:** `ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_V2_1.pdf` · 58 páginas A4
**Paquete:** `PAQUETE_ATLAS_V21_REVISION.zip`
**Base:** `INFORMEFINAL/claude/atlas_22_edicion_institucional_v1/` (intacta; no se tocó un byte)
**Edición anterior:** `..._V2.pdf` y `PAQUETE_ATLAS_V2_REVISION.zip` quedan en esta carpeta
sin modificar. V2.1 no los reemplaza: los corrige.
**Destinatario:** equipo del Ministro · **Fecha:** 2026-08-03

Ninguna cifra, universo, cota, proporción, saturación ni decisión territorial se recalculó.
El control automático `qa/DIFF_CIFRAS_V1_V2.csv` compara la firma numérica de cada campo de
las 22 fichas contra V1: **88 comparaciones, 88 PASS**. La prosa cambia a propósito; los
números no se mueven.

---

# V2.1 · Respuesta a la auditoría externa del PAQUETE_ATLAS_V2_REVISION

Doce correcciones pedidas. **Diez ejecutadas, dos rechazadas con fundamento** —y el rechazo
era, en esos dos casos, lo que la propia auditoría pedía—. Los dos bloqueos que siguen
abiertos se declaran como tales.

## Qué quedó hecho

1. **B-01 · p5 sin una sola etiqueta cortada.** Las quince cadenas partidas a mitad de
   palabra ("Polo documentad", "Microcent", "Referenc") venían de un bucle que recortaba de a
   dos caracteres sin dejar marca. La página pasa de tres columnas estrechas a **una
   referencia por renglón a ancho completo**: la etiqueta más larga del corpus —"Polo
   documentado sin unidad espacial estabilizada", 68 caracteres— entra entera, con margen.
   No hubo que acortar ninguna etiqueta "con criterio": no hizo falta acortar ninguna.

2. **B-02 · control de TEXTO CLIPEADO en el QA, por tres vías independientes.** Cualquiera
   de las tres hace fallar la producción:
   - **palabra_truncada** — se construye el vocabulario de todo lo que el generador puede
     dibujar (los literales de los tres scripts leídos por AST, el JSON canónico, los
     rótulos de las capas geométricas y las matrices) y se marca toda palabra del PDF que
     sea prefijo estricto de una palabra real sin ser ella misma una palabra real. Es la vía
     que habría cazado "Microcent" en V2.
   - **fuera_de_caja** — ninguna cadena del PDF puede sobresalir del área imprimible de su
     página; se recorren los spans de las 58 páginas con su caja real.
   - **acorte_sin_marca** — todo acortamiento deliberado pasa ahora por una única función
     (`ajustar_a_ancho`), que corta en límite de palabra y deja elipsis; y el propio código
     del generador se audita para que el modismo que causó el defecto —recortar de a
     caracteres dentro de un `while` sobre `stringWidth`— no pueda volver sin dejar marca.

   **El control encontró dos defectos más que la V2 había publicado**, además del que motivó
   B-01: la definición de familia de la p5 se salía del margen derecho en las familias de
   nombre largo, y el Anexo D cortaba "Rojas–Honor…" a mitad de palabra. Los dos, corregidos.
   El QA pasa de 25 a 26 controles, los 26 en PASS.

3. **M-01 · el mapa general ocupa la página.** La tabla de las 22 baja al pie en dos
   columnas y el mapa toma el ancho completo. El dibujo pasa de unos 126 × 142 mm a
   180 × 181 mm: **+62% de superficie**, sin tercio inferior vacío. Cada fila de la tabla
   sigue enlazada a su ficha.

4. **M-02 · anclas geográficas.** Número de las 15 comunas sobre el gris, **Río de la
   Plata**, **Av. Gral. Paz** —trazado real del callejero oficial GCBA, resaltado y
   rotulado— y **Riachuelo** sobre el borde sur. El número de comuna se aparta cuando cae
   sobre el disco numerado de una referencia: manda la referencia.

5. **M-03 · la advertencia que faltaba**, junto a las notas del mapa general y en color de
   acento: *"El tamaño del área no indica la cantidad de oferta: depende de cuán dispersos
   estén los registros."* Verificado contra las capas entregadas: Devoto ocupa 4,787 km² con
   119 registros y Villa Crespo 3,355 km² con 646. La geometría no se tocó; se dice lo que
   significa.

6. **F-01 · calles rotuladas en los mapas de ficha.** Cada mapa rotula las calles que su
   propia línea "Qué muestra este mapa" nombra, tomadas del callejero oficial GCBA: Thames y
   Gurruchaga en la p22, Corrientes/Callao/9 de Julio en la p11, Jorge Newbery y Dorrego en
   la p25, y así. Son **basemap, no producto**: gris, sin color de familia, sin entrar en
   ninguna envolvente. `qa/QA_ROTULOS_CALLES.csv` registra qué se rotuló en cada página.

7. **F-02 · el aire recuperado en las fichas de página entera.** El cuerpo y la separación
   entre bloques se ajustan a la columna real de cada ficha —se prueba el cuerpo más grande
   que todavía entra y el sobrante se reparte entre los bloques— y la línea de fuente se
   ancla al pie. Las páginas 21, 30, 44 y 47 llegan al pie; también la 49, que arrastraba lo
   mismo. `qa/QA_AJUSTE_FICHAS.csv` deja registrado el ajuste aplicado a cada ficha.

8. **D-01 · R04 Puerto Madero sin los diques. BLOQUEADO-01 cerrado.** Se integró la
   sustracción del paquete de desbloqueos: se resta la intersección de la máscara con R04,
   no la máscara completa. **3,369573 km² → 3,145412 km²**, exactamente la cifra que la
   auditoría verificó. La fuente se declara como OpenStreetMap/Overpass (ODbL 1.0) validada
   contra la capa oficial de IDECABA con 97,113% de coincidencia; la línea "Qué no es" de la
   p15 dice ahora que el área **excluye** el espejo de agua; y el generador **falla** si la
   máscara llega a tocar cualquier referencia que no sea R04.

9. **D-02 (la parte que no decide nada) · Monroe y Congreso rotuladas en la p39** como
   calles de referencia del callejero oficial, sin dibujarlas como ejes de producto.
   Desaparece la disonancia entre la ficha, que nombra tres ejes, y el mapa, que dibujaba uno.

10. **R-01 y R-02 · el registro.** La aritmética de D-A-05 quedó corregida —el error era
    omitir un paso, no una cifra mal medida— y "la autoridad institucional" dejó de ser
    sujeto de las frases: ahora se refiere la instrucción (T-1, T-2, T-3) o "la conducción
    del proyecto".

## Qué quedó a medias

1. **La p21 (R08) llega al pie, pero con separaciones generosas entre bloques.** Su ficha es
   genuinamente corta: aun con el cuerpo en su máximo razonable, llenar la columna exigió
   repartir el sobrante en separaciones amplias. Se ve deliberado, no truncado, pero es una
   página con menos densidad que sus vecinas.

2. **En R02 y R14 el rótulo de calle repite el nombre de la referencia** ("Av. Corrientes"
   en gris sobre el corredor "Avenida Corrientes" en azul). Se conservó porque cumplen
   funciones distintas —uno marca por dónde corre la avenida, el otro nombra el área—, pero
   es una redundancia visible.

3. **Las vistas de detalle de R12 y R19 siguen pareciéndose a su mapa principal.** Aportan
   zoom y rótulos, no una capa de información nueva. Sin cambios respecto de V2.

4. **R09 y R10 siguen dibujando menos que su cifra** (226 de 327 y 266 de 907). Es la
   consecuencia buscada de no fusionar focos independientes, y ambas páginas lo dicen.

## Qué directamente no se hizo, y por qué

1. **D-02 · NO se integraron los ejes Monroe y Congreso de R17.** Las alternativas incluyen
   40-50 de 189 puntos (Monroe) y 18-26 (Congreso): adoptar cualquiera convertiría una regla
   analítica en un eje institucional que el corpus nunca cerró. **BLOQUEADO-02 sigue
   abierto.** Es la respuesta correcta, no una deuda.

2. **D-03 · NO se integró el radio de 300 m como núcleo de R15.** Un buffer alrededor del
   centroide de una plaza no es un núcleo gastronómico, y con 25 de 119 puntos adentro es el
   mismo caso que el disco de R18. **BLOQUEADO-03 sigue abierto.** Del paquete se incorporó
   lo único que aporta sin decidir nada: la confirmación, con Espacios Verdes GCBA, de que
   Plaza Arenales está en Villa Devoto, Comuna 11 —lo que valida la denominación "Devoto"
   que el Atlas ya usaba—. Anotado en el registro; no cambia el mapa ni la cifra.

3. **Las cinco familias siguen sin distinguirse por color en impresión en blanco y negro.**
   Es matemáticamente imposible con cinco rellenos translúcidos; se resolvió por trama, como
   en V2.

4. **R18, R20 y el tramo de R02 siguen sin identificarse por su relleno en el mapa general.**
   Por debajo de unos 10 mm en página ningún recurso de relleno es legible: se identifican
   por el número y la tabla.

---

## Lo que no cambió, y se verificó que no cambió

Ninguna cifra, universo, cota, proporción, saturación ni decisión territorial se recalculó.
`qa/DIFF_CIFRAS_V1_V2.csv` sigue comparando la firma numérica de cada campo de las 22 fichas:
**88 comparaciones, 88 PASS**. La única geometría que cambió es la de R04, por la sustracción
de agua de D-01, y R04 no tiene cifra canónica comparable.

---

## La validación más fuerte de esta fase

Al reconstruir la cartografía desde los vectores originales apareció una coincidencia que no
estaba documentada y que **verifica el corpus de punta a punta**: los puntos observados
coinciden exactamente con las cifras que publican las fichas.

| Referencia | Cifra de la ficha | Puntos en la capa fuente |
|---|---|---|
| R08 Villa Crespo | 646 | 646 (Z01, universo deduplicado) |
| R09 Chacarita | 327 | 327 (Z02) |
| R10 Caballito | 907 | 907 (Z03) |
| R11 Boulevard Caseros | 66 | 66 (Z04) |
| R14 Avenida Boedo | 79 | 79 (Z07, porción E-PLACES) |
| R15 Devoto | 119 | 119 (Z08, porción E-PLACES) |
| R16 Donado–Holmberg | 40 | 4 propios + 36 compartidos con Z10 |
| R17 Villa Urquiza | 189 | 153 propios + 36 compartidos con Z09 |

Las envolventes de esas ocho referencias se dibujan **sobre los mismos puntos que su cifra
cuenta**. No es una equivalencia impuesta: la reconstrucción partió de la geometría y llegó
al mismo número que la ficha traía escrito desde otra rama del trabajo.

---

## B2 · Envolvente editorial única para las 22

**Antes.** Tres familias visuales incompatibles: cinco mapas editoriales, nueve figuras
primitivas (rectángulos, círculos, cápsulas, rombos con la grilla de cálculo dibujada
adentro) y ocho salidas técnicas crudas con nube de puntos de colores, punteados violetas y
tablas de convenciones internas.

**Ahora.** Una sola función produce las 29 vistas. Buffer parametrizable sobre puntos
observados, cierre morfológico, simplificación topológica y suavizado de Chaikin. Buffer por
defecto 200 m, con cuatro excepciones aprobadas: R11 120 m, R10 150 m, R16 y R19 conservan
sus 200 y 250 m originales.

**Recorte mutuo por línea media.** Diagrama de Voronoi sobre las formas dibujadas, disolución
por referencia e intersección de cada envolvente con su propia región. **17 pares tenían
solape real; los 15 independientes quedaron en 0 m²**. El mayor era R16/R17 con 1.262.000 m²
—Donado–Holmberg contra Villa Urquiza, justo lo que el corpus prohíbe fusionar por escrito.

**Dos exenciones, ambas por declaración del corpus** (`qa/QA_SOLAPES_22.csv` las registra con
su motivo): R12/R18, que el corpus define como una geometría compartida con dos productos
separados; y R02/R12, porque Corrientes atraviesa físicamente el Centro y ninguna ficha
declara que el corredor sea discontinuo. R19 **no** se exentó: la ficha de R09 dice "sin
fusión con R19" y ese par sigue recortado.

**Casos especiales resueltos.** R18 conserva su disco de 400 m, sin punto central y rotulado
como radio de consulta. R22 no se suaviza y pierde la grilla de cálculo. R20 conserva sus
extremos planos y solo ablanda las esquinas. R21 pierde los puntos de anclaje del buffer.
R04 deja de estar recortado contra el marco. R09 y R10 se dibujan por subunidad declarada,
de modo que sus focos independientes dejan de fundirse en una mancha.

**Todo vectorial.** Los 29 mapas se dibujan como trazos nativos del PDF: cero imágenes
rasterizadas (control `sin_imagenes_embebidas` en PASS). Los PNG originales de
`cartografia_22_correccion_visual_v1/` no se tocaron; se leyeron sus fuentes aguas arriba.

## B1 · Mapa general de la Ciudad

**Antes.** La p6 era una hoja de contactos con 22 miniaturas de ~35 mm de las propias páginas
de mapa. En 58 páginas no había una sola vista de la Ciudad.

**Ahora.** Mapa de CABA a página completa: contorno de la Ciudad, comunas en gris muy tenue,
las 22 referencias con su forma real coloreadas por familia y numeradas, tabla lateral de 22
filas enlazada a cada ficha, leyenda de familias y nota de aproximación. Sigue siendo la
página 6 y el total sigue siendo 58.

## B3 · Bloque inferior

**Antes.** Cuatro capas que decían casi lo mismo o nada: "Lectura y límites" con
instrucciones internas al equipo, "Convenciones comunes" con cuatro rótulos sin muestra de
color, "Caveat geométrico" repitiendo el descargo y "Fuente/versión" con CRS y nombre de
carpeta.

**Ahora.** Tres líneas rotuladas, idénticas en las 29 páginas: **Qué muestra este mapa ·
Qué mide la cifra · Qué no es**. Las 22 redacciones se derivan del JSON canónico y su origen
campo por campo está en `qa/TRAZABILIDAD_TEXTOS_B3.csv` (87 filas). Al lado, una leyenda real
con muestra de color que solo anuncia lo que el mapa dibuja.

CRS, versión, fuente y fecha de corte se movieron al anexo de trazabilidad (p. 58). Las
instrucciones internas ("No absorber…", "No extender a…", "Z03-S4 fue retirado…") se movieron
al Anexo C de controles y exclusiones (p. 54). No se perdió nada: cambió de lugar.

## B4 · Formato y layout

- Marca y título duplicados dentro de los mapas: **eliminados** de raíz (ya no hay raster).
- Descargo triplicado → **uno solo por página**, al pie, en cuerpo chico. Verificado página
  por página: 29 páginas con exactamente una aparición, cero con dos.
- El mapa ocupa el ancho útil completo y el bloque inferior se dimensiona midiendo el texto
  real: se recuperó el tercio inferior muerto.
- p. 46 (Lacroze–Cabildo): el gráfico cortado y el orden invertido de bloques **resueltos**.
- p. 13: el vacío superior **resuelto**.
- p. 3: el índice corta por sección, así que "Vistas de detalle" ya no queda huérfano al pie
  de columna con una sola entrada.
- Escala: dos escalas normalizadas (250 m / 500 m), siempre rotuladas.
- Códigos internos → nombre en castellano, tomado del campo `nombre` de las capas del corpus:
  C-S01 → Microcentro financiero, LAC-T1 → tramo Libertador–Cabildo, R21-OESTE → red
  occidental de calles documentadas, y así. Control `sin_codigos_internos` en PASS.
- Jerga técnica fuera de las páginas públicas. Control `sin_jerga_tecnica` en PASS.
- "INFORMEFINAL" y "EPSG:5347" fuera de las páginas.
- **Badge de cifra con clave visual**: cada naturaleza tiene fondo, barra de acento y símbolo
  propios — `=` cifra exacta, `≥` cota inferior, `◷` antecedente previo — y la ausencia de
  cifra deja de ser un badge.

## B5 · Contenido ejecutivo

- **p. 2 reescrita.** Antes: cinco viñetas de metodología, cero números. Ahora abre con
  22 referencias en 11 de las 15 comunas, cinco familias territoriales y las cifras agrupadas
  por método comparable, con la advertencia de no-comparabilidad al lado del dato.
- **p. 5: 22 tipologías → 5 familias** (polo, polo con subzonas o partes, eje o corredor, área
  segmentada, referencia dispersa), con la etiqueta fina conservada junto a cada referencia.
  Esas familias son las que dan el color en el mapa general.
- **"Sin cifra canónica comparable" baja de jerarquía**: pasa de titular naranja de 20 pt a
  línea secundaria en cuerpo normal. Cinco de las seis primeras fichas ya no abren diciendo
  que no hay número.
- Las secciones negativas se reordenaron y renombraron: "Límites" en rojo pasó a "Qué no se
  puede concluir" en cuerpo secundario, después de la evidencia.

## B6 · QA

- **25 controles automáticos, 25 en PASS**, incluidos los de cierre: 58 páginas A4 exactas
  sin páginas vacías, cero "DataGastro", cero jerga técnica, cero códigos internos, cero
  "Convenciones comunes"/"Lectura y límites"/"Caveat geométrico", un solo descargo por página,
  cero caracteres mal codificados, tildes intactas, sin fusiones indebidas, enlaces internos
  y 47 marcadores funcionando.
- **`qa/QA_VISUAL_INSPECCION_58.csv`: 58 de 58 filas con hallazgo real.** Cero PENDIENTE.
  50 páginas OK y 8 con observación declarada.
- `qa/QA_PRESERVACION_INSUMOS.csv`: los insumos canónicos conservan su SHA-256.
- `qa/QA_PRIVACIDAD_V2.csv`: nueve controles en PASS sobre el PDF y sobre el paquete.

---

## Qué quedó hecho en V2 (histórico)

1. Las 29 vistas comparten una sola estética editorial, dibujadas como vectores del PDF.
2. Recorte mutuo aplicado: ninguna referencia declarada independiente aparece fusionada.
3. Mapa general de la Ciudad en la p. 6, con tabla lateral enlazada.
4. Bloque inferior de tres líneas en las 29 páginas, trazable al JSON canónico.
5. Un solo descargo por página; el resto de la metodología, en los anexos.
6. Códigos internos y jerga técnica fuera de las páginas públicas.
7. Badge de cifra con clave visual por naturaleza.
8. Resumen ejecutivo con datos de la Ciudad y 22 tipologías colapsadas en 5 familias.
9. Inspección visual real de las 58 páginas.
10. Paleta verificada en escala de grises: la paleta aprobada fallaba 6 de 10 pares, y se
    resolvió agregando trama por familia sin cambiar los colores.
11. Registro de decisiones autónomas llevado durante la ejecución: `qa/DECISIONES_AUTONOMAS_V2.md`.

## Qué quedó a medias en V2 (histórico; los puntos 1 y 6 se resolvieron en V2.1)

1. **R04 Puerto Madero incluye los diques.** Se recortó contra la tierra barrial oficial
   (–0,807 km², la porción sobre el Río de la Plata), pero el polígono barrial oficial
   contiene los espejos de agua interiores. Falta una capa de hidrografía: no existe en el
   repositorio. Los proxies disponibles recortarían también plazas y parques, cosa
   expresamente vetada. → BLOQUEADO-01.
2. **R17 Villa Urquiza muestra un eje de tres.** La ficha nombra Triunvirato, Monroe y
   Congreso; solo Triunvirato tiene trazado cerrado en el corpus. El mapa dice explícitamente
   que muestra el único con geometría. → BLOQUEADO-02.
3. **La vista de detalle de R15 repite el polo completo.** El corpus no cerró geometría para
   el núcleo de Plaza Arenales, así que la vista amplía y lo declara. → BLOQUEADO-03.
4. **Las vistas de detalle de R12 y R19 se parecen mucho a su mapa principal.** Aportan zoom
   y rótulos de componentes, pero no una capa de información nueva. Declarado en las filas
   32 y 46 de la inspección visual.
5. **R09 y R10 dibujan menos que su cifra.** Al envolver por subunidad declarada, el área
   cubre 226 de 327 registros en Chacarita y 266 de 907 en Caballito. Es la consecuencia
   buscada de no fusionar focos independientes, y la línea "Qué mide la cifra" lo dice en
   ambas páginas.
6. **Cinco fichas conservan aire en el tercio inferior** (páginas 21, 30, 44, 47 y 49). No
   afecta la lectura; se optimizó el layout de las páginas de mapa, no el de las fichas.

## Qué directamente no se pudo hacer en V2 (histórico; el punto 1 se resolvió en V2.1)

1. **Recortar los diques de Puerto Madero** — falta la capa oficial de hidrografía de GCBA.
   Con esa capa en el repositorio, el recorte es una línea de código y no toca ninguna cifra.
2. **Dibujar los ejes Monroe y Congreso de R17** — no existen como geometría en ninguna capa
   cerrada. Construirlos desde el callejero sería producir geometría que el corpus nunca
   cerró.
3. **Delimitar el núcleo de Plaza Arenales en R15** — mismo motivo.
4. **Que las cinco familias se distingan por color en impresión en blanco y negro** — es
   matemáticamente imposible con cinco rellenos translúcidos y colores institucionales
   saturados. Se resolvió por otra vía (trama por familia), no por color.
5. **Que R18, R20 y R02 se identifiquen por su relleno en el mapa general** — por debajo de
   unos 10 mm en página ningún recurso de relleno es legible. Se identifican por el número y
   la tabla lateral.

---

## Reproducción

Desde la raíz del repositorio, sin red:

```
.venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_geometrias_editoriales_v2.py
.venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_atlas_v2.py --finalize-visual
```

El primero deriva las capas geométricas y aplica la sustracción de agua de R04; el segundo
verifica los seis insumos canónicos por SHA-256, arma el PDF, corre los 26 controles —incluido
el de texto clipeado— y empaqueta.

El primero deriva las capas geométricas desde las fuentes cerradas del corpus; el segundo
verifica los seis insumos canónicos por SHA-256, arma el PDF, corre el QA y empaqueta.
Ambos rechazan cualquier destino que no sea `outputs/polos_gastro/ATLAS_V2/`.
