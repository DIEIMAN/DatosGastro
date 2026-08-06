# PLAN ATLAS V2 — legibilidad institucional y cartografía poligonizada

**Fase:** ATLAS_V2 · **Estado:** PLAN — ETAPA 1, sin ejecución
**Fecha:** 2026-08-03 · **Destinatario del producto:** equipo del Ministro (no técnico)
**Base:** `outputs/polos_gastro/INFORMEFINAL/claude/atlas_22_edicion_institucional_v1/`
(58 pp, PDF `ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS.pdf`)

Este documento es solo el plan. **No se modificó ningún archivo del Atlas.** El único
archivo escrito en esta etapa es este PLAN y el directorio que lo contiene.

---

## BLOQUE 0 — Verificación previa: qué existe realmente

### 0.1 Generador y contenido — CONFIRMADOS

| Artefacto | Ruta | Estado |
|---|---|---|
| Generador | `.../atlas_22_edicion_institucional_v1/scripts/build_atlas_edicion_institucional.py` | Existe, 2.161 líneas, legible |
| Contenido | `.../contenido/contenido_atlas_22_v2_compacta.json` | Existe, 1.086 líneas; 22 fichas + 7 complementarias + anexos |
| PDF actual | `.../ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS.pdf` | 58 pp, A4 exacto (210×297 mm), 47 marcadores |
| Renders 58 pp | `.../qa/render_paginas/pagina_01..58.png` | Existen, 150 dpi |

Los **6 insumos canónicos con hash congelado** que el generador valida antes de escribir
(Atlas V1 PDF y ZIP, auditoría V1, cierre V1.1, ZIP cartografía, ZIP fichas) fueron
verificados uno por uno: **los 6 dan OK**. Las tipografías resuelven por
`.venv/Lib/site-packages/matplotlib/mpl-data/fonts/ttf` (DejaVu Sans presente). El
generador es **reproducible hoy, sin red**.

### 0.2 Geometrías vectoriales — **EXISTEN PARA LAS 22 REFERENCIAS**

Esta era la pregunta crítica. La respuesta es **sí, hay vectores**, pero no en el paquete
del Atlas: están aguas arriba. El paquete de cartografía
(`cartografia_22_correccion_visual_v1/`) solo distribuye PNG 1600×2000 + SVG con el raster
embebido — pero su generador
(`cartografia_22_v1/scripts/build_cartografia_22_v1.py`, 636 líneas, geopandas + shapely)
documenta de dónde salió cada forma. Seguí esas rutas y verifiqué que cada capa abre.

**Inventario verificado (todas las capas se abrieron y se contaron sus entidades):**

| Ref | Geometría vectorial de origen | Tipo | Puntos con lat/lon |
|---|---|---|---|
| R01 Palermo | `scripts/polos_gastro/build_fase24_fase22_corregida_oficina.py` → `GEOMETRIES` (coords inline, EPSG:4326) | 3 polígonos (Soho, Hollywood, Cañitas) | — |
| R02 Corrientes | ídem | 1 línea + 1 hito | — |
| R03 San Telmo | ídem | 1 polígono + 1 línea + 1 hito | — |
| R04 Puerto Madero | ídem | 2 polígonos + 1 línea + 1 hito | — |
| R05 Belgrano | `correcciones_cartograficas_post_qa_v3_1/capas/BELGRANO_PRESENTACION_V3_1.geojson` | 3 piezas (2 MultiPolygon + 1 Polygon) | 697 (`PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson`) |
| R06 Recoleta | `.../RECOLETA_PRESENTACION_V3_1.geojson` | 1 Polygon | 767 |
| R07 Costanera Norte | `.../COSTANERA_NORTE_PRESENTACION_V3_1.geojson` | 4 piezas | 72 |
| R08 Villa Crespo | `tanda1_saturaciones_v4_4/outputs/SUBUNIDADES_CORREGIDAS_V4_4.geojson` (Z01) | polígonos + ejes | **646** (Z01) |
| R09 Chacarita | ídem (Z02) | polígonos + ejes | **327** (Z02) |
| R10 Caballito | ídem (Z03) | polígonos + ejes | **907** (Z03) |
| R11 Blvd. Caseros | ídem (Z04) | polígono + eje | **66** (Z04) |
| R12 Centro | `preflight_tecnico_grupo_a_v1/areas/AREAS_PROVISIONALES_GRUPO_A.geojson` | 7 subunidades | — (universo *hasheado*) |
| R13 Abasto | ídem | 1 polígono | — (hasheado) |
| R14 Av. Boedo | `tanda2_ejecucion_v1/config/AREAS_TANDA2_ANALISIS_REPARADAS.geojson` (Z07) + `CLUSTERS_BASELINE_TANDA2_V1.geojson` | área + eje + clusters | **271** (Z07) |
| R15 Devoto | ídem (Z08) | área + clusters | **623** (Z08) |
| R16 Donado–Holmberg | ídem (Z09) | doble eje buffer 200 m + clusters | 9 propios + 125 compartidos Z09\|Z10 |
| R17 Villa Urquiza | ídem (Z10) | área + clusters | **761** (Z10) |
| R18 Esmeralda–Paraguay | `AREAS_PROVISIONALES_GRUPO_A.geojson` (`GA-R18-CS07-COMPARTIDA`) | **disco r=400 m** por construcción | — (hasheado) |
| R19 Lacroze | `preflight_tecnico_grupo_b_reparado_v1/areas/AREAS_PROVISIONALES_GRUPO_B.geojson` | 2 tramos (buffer 250/225 m) + control | — (hasheado) |
| R20 García del Río | `preflight_tecnico_grupo_c_correccion_v1/areas/R20_PRODUCTO_CORREGIDO.geojson` | banda plana 180 m | — (hasheado) |
| R21 La Paternal | `AREAS_PROVISIONALES_GRUPO_B.geojson` | 2 áreas (unión de buffers 300 m) + control | — (hasheado) |
| R22 Villa Pueyrredón | `preflight_tecnico_grupo_c_v1/areas/AREAS_PROVISIONALES_GRUPO_C.geojson` + `CELDAS_R22_BASE.geojson` | marco barrial + 14 celdas | — (hasheado) |

**Base cartográfica de CABA para el mapa general (B1) — existe:**
`data/raw/geo_comunas.geojson` (15 entidades) y `data/raw/geo_barrios.geojson` (48).

**Puntos: sin datos personales.** Las capas de puntos traen `point_id_sanitizado` /
`place_hash` / `lugar_hash`, `lat`, `lon`, categoría y fuente. No hay nombres, CUIT, DNI,
teléfonos, mails ni montos. Cumplen la regla 8.

**Entorno geométrico verificado:** shapely 2.1.2 (GEOS 3.13.1, `voronoi_polygons`
disponible), geopandas 1.1.3, reportlab 5.0.0 (dibuja paths vectoriales nativos),
matplotlib 3.11, PyMuPDF, scipy 1.18.

### 0.3 Los tres hallazgos de Bloque 0 que **cambian el plan**

**H-1 — Ocho referencias no tienen puntos: R12, R13, R18, R19, R20, R21, R22 (y R02).**
Sus universos se guardaron *hasheados* (solo `place_hash` + producto) por privacidad. Para
ellas **la receta de B2 “buffer generoso sobre los puntos” es materialmente imposible**: no
hay puntos que envolver. Lo que existe es la geometría operativa con que se consultó
(disco de 400 m, banda de 180 m, buffers de 250/225/300 m, marco barrial). Para estas ocho
la envolvente editorial solo puede ser un **suavizado morfológico de esa geometría ya
decidida**, no un re-envolvente de observaciones. Esto no rompe nada, pero significa que
**R18 no puede dejar de ser un disco sin inventar una forma**: ver decisión D-5a.

**H-2 — El QA de texto no ve la jerga porque la jerga es imagen.** Verifiqué el texto
seleccionable de las 58 páginas: **cero apariciones** de DataGastro, HDBSCAN, epsilon, ARI,
Jaccard, businessStatus, NO_EVALUABLE, INFORMEFINAL, EPSG, «Convenciones comunes»,
«Lectura y límites», «Caveat». Todo eso está **dentro de los PNG**, fuera del alcance de
cualquier grep. Corolario: el control de cierre de B6 solo será real si se ejecuta sobre un
PDF donde ese texto sea texto — es decir, **B6 depende de B2**, no es independiente.

**H-3 — El generador de cartografía original ya no corre.** `build_cartografia_22_v1.py`
lee `outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson`,
ruta que hoy no existe: el archivo se movió a
`outputs/polos_gastro/FASE5-29/fase15_mapas_callejeros_v3/assets/`. No es bloqueante (no
vamos a re-ejecutar ese paquete), pero el callejero **sí** hace falta para B1/B2 y hay que
apuntar a la ruta nueva.

### 0.4 Diagnóstico de la auditoría — verificado, no re-descubierto

Confirmé contra los renders y el código: **A** (p6 es una hoja de contactos de 22
miniaturas de ~35 mm — `create_locator()` recorta cada PNG y lo pega en una grilla 4×6; no
hay ninguna vista de CABA en 58 páginas), **B** (las tres familias visuales existen y su
origen está explicado por `SOURCES` del script de cartografía: las Familia C son PNG
técnicos embebidos con `imshow`), **C1–C4** (marca y título duplicados dentro del PNG —
visible en p22; descargo triplicado; tercio inferior vacío), **C5** (p46 con el gráfico
cortado al pie y sin eje X), **C6** (p3: «Vistas de detalle» queda al pie de la columna 2
con una sola entrada, sus otras seis siguen en la columna 3 sin encabezado), **C13** (las
58 filas de `QA_VISUAL_INSPECCION_58.csv` dicen `PENDIENTE_INSPECCION_VISUAL` mientras
`QA_VISUAL_PRODUCTOR.md` declara «QA del productor completo»), **E** (p2 no tiene un solo
número; las 22 tipologías son 22 etiquetas distintas; `cifra` = `SIN_CIFRA_CANONICA_COMPARABLE`
en R01, R02, R03, R04 y R06).

Dato útil que ya está en el JSON y no hay que construir: cada ficha trae `naturaleza` con
exactamente cuatro valores — `exacta` (8 refs), `cota_inferior` (8), `historica_metodologica`
(3), `no_localizada` (3). **Esa es la clave visual del badge de C12/B4, sin inventar nada.**

### 0.5 Superficies protegidas — leídas y respetadas

`docs/polos_gastro/PROTECTED_SURFACES.yaml` marca como `puede_modificar: false` a
`cartografia_22_correccion_visual_v1/**`, `cartografia_22_v1/**`, `fichas_22_v1/**`,
`atlas_22_v1/**`, `atlas_22_v2_compacta_*/**`, `tanda1*/**`, `tanda2*/**`,
`build_fase25_*.py` y los globales de INFORMEFINAL. **Todos los insumos de 0.2 son de solo
lectura.** Todo lo nuevo se escribe exclusivamente en `outputs/polos_gastro/ATLAS_V2/`.

> **Nota de ciclo (CICLO_OPERATIVO_UNA_PASADA).** `ESTADO_GENERAL_INFORMEFINAL.md` declara
> `P-ATLAS-V2-COMPACTA` **CERRADO** y `atlas_22_v2_compacta_correccion_local_v1` como fuente
> pública vigente. Esta fase **no reabre** ese cierre: produce una **edición V2 nueva y
> paralela** en `ATLAS_V2/`, con el V1 institucional intacto. La actualización del estado
> global, si corresponde, es decisión tuya al cierre, no de esta fase.

---

## Bloques de trabajo

Directorio de la fase (todo lo nuevo va acá):

```
outputs/polos_gastro/ATLAS_V2/
├── PLAN_ATLAS_V2.md               ← este archivo
├── CAMBIOS_V2.md                  ← entregable final
├── ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_V2.pdf
├── scripts/
│   ├── build_geometrias_editoriales_v2.py   ← B2 (capa geométrica)
│   └── build_atlas_v2.py                    ← derivado del generador V1
├── contenido/contenido_atlas_v2.json        ← copia + textos B3/B5
├── capas/                                   ← GeoJSON derivados (B2)
├── assets/                                  ← si queda algún raster
└── qa/                                      ← B6
```

### B1 — Mapa general de la Ciudad *(reemplaza la p6)*

**Toca:** `scripts/build_atlas_v2.py` (nueva `draw_mapa_general()`, elimina
`create_locator()`), `capas/envolventes_editoriales_v2.geojson`, `data/raw/geo_comunas.geojson`
y `geo_barrios.geojson` (lectura).

**Hace:** una página A4 completa con contorno de CABA, comunas en gris muy tenue, costa y
Riachuelo como anclas; las 22 envolventes de B2 con su forma real, coloreadas por familia
(B5) y numeradas R01–R22; tabla lateral de 22 filas (número · nombre · página) con enlace
interno a cada ficha; nota de escala. Si el norte queda apretado (Palermo/Chacarita/Villa
Crespo/Paternal), dos recuadros de zoom (Norte y Centro) **dentro** de la misma página.

**Depende de B2** (necesita las envolventes). Se implementa después de B2 aunque sea el
bloque de máxima prioridad de producto.

**Aceptación:** la p6 es un mapa de CABA a página completa; las 22 formas se distinguen y
se leen sus números; las 22 filas de la tabla enlazan y los destinos son correctos; ninguna
etiqueta tapada; el total sigue siendo 58 páginas (salvo decisión D-3).

---

### B2 — Envolvente editorial única para las 22

**Toca:** `scripts/build_geometrias_editoriales_v2.py` (nuevo), `capas/*.geojson` (nuevo),
`scripts/build_atlas_v2.py` (renderer vectorial nuevo, reemplaza `derive_maps()` y
`draw_map_page()`).

**Pipeline, en dos caminos según H-1:**

*Camino A — 14 referencias con puntos* (R01, R05, R06, R07, R08, R09, R10, R11, R14, R15,
R16, R17 y las que tengan geometría propia + observaciones):
1. tomar puntos y/o ejes de la referencia;
2. buffer parametrizable (default D-1);
3. unión + cierre morfológico `buffer(+d).buffer(−d)`;
4. simplificación topológica + suavizado Chaikin;
5. multiparte donde el corpus lo exige (R07, R09, R16, R19): piezas separadas del mismo
   color, **nunca** unidas.

*Camino B — 8 referencias sin puntos* (R02, R12, R13, R18, R19, R20, R21, R22): la
envolvente es el **suavizado morfológico de la geometría operativa ya cerrada** — mismos
pasos 3–5, sin paso 1–2. Se preserva la geometría decidida; solo cambia su acabado visual.
R21 pierde los puntos de anclaje dibujados; R22 pierde la grilla de cálculo; R20 deja de
ser un rectángulo de esquinas vivas; R04 deja de estar recortado contra el marco.

**Recorte mutuo (restricción crítica).** Antes de dibujar: `shapely.voronoi_polygons` sobre
los vértices densificados de los **núcleos** (geometría pre-buffer) de todas las
referencias → disolver celdas por `referencia_id` → intersecar cada envolvente con su
propia región. Resultado: áreas generosas que **nunca se fusionan** con la vecina y respetan
«No absorber Donado–Holmberg», «sin fusión con R19, Palermo o Villa Crespo», «No extender a
Patricios o Barracas». Se emite `qa/QA_SOLAPES_22.csv` con la matriz de intersecciones: el
criterio de aceptación es **0 m² de intersección entre referencias que el corpus declara
independientes**.

**Render:** paths vectoriales nativos en reportlab; títulos, rótulos, leyenda y escala como
**texto real del PDF** (D-2). Los PNG de `cartografia_22_correccion_visual_v1/` quedan
intactos: se leen sus fuentes aguas arriba, nunca se sobrescriben.

**Aceptación:** las 29 vistas comparten una sola estética; `QA_SOLAPES_22.csv` sin fusiones
indebidas; el texto de los mapas aparece en la extracción de texto del PDF; los PNG fuente
conservan su SHA-256; ninguna cifra tocada.

---

### B3 — Bloque inferior: reemplazo completo

**Toca:** `contenido/contenido_atlas_v2.json` (22 tríos de texto nuevos, derivados de
`caracterizacion` / `detalle_cuantitativo` / `limitaciones_especificas` ya existentes),
`scripts/build_atlas_v2.py`.

**Hace:** elimina «Lectura y límites», «Convenciones comunes», «Caveat geométrico» y
«Fuente/versión» de la página. En su lugar, tres líneas rotuladas idénticas en las 29
páginas: **Qué muestra este mapa** · **Qué mide la cifra** · **Qué no es**. Cuando no hay
cifra comparable, la línea del medio va en positivo: «Referencia caracterizada; sin conteo
comparable entre métodos.» Al lado, leyenda real de 3–4 ítems **con muestra de color**:
*área de la referencia · componente interno · eje · punto de referencia*.

**Reubicaciones (nada se pierde):** CRS, versión, fuente, fecha de corte y metodología → al
anexo de trazabilidad (p58, ya existe). Instrucciones internas («No absorber…», «No
extender a…», «Z03-S4 fue retirado…») → al Anexo C de controles y exclusiones (p54, ya
existe).

**Aceptación:** cero apariciones de los cuatro bloques viejos; las 29 páginas tienen el
mismo trío; las 22 redacciones son trazables línea a línea al JSON de origen (se emite
`qa/TRAZABILIDAD_TEXTOS_B3.csv`); ninguna afirmación nueva sobre el territorio.

---

### B4 — Formato y layout

**Toca:** `scripts/build_atlas_v2.py`.

- Marca y título duplicados dentro de los mapas: **eliminados** (quedan solo en el
  encabezado de página). Resuelto de raíz por B2: el título ya no se dibuja dentro del mapa.
- **Un solo descargo** por página, al pie, en cuerpo chico.
- Mapa ampliado al ancho útil completo, recuperando el tercio inferior muerto.
- p46: gráfico completo con su eje X y orden de bloques alineado al de las otras vistas.
- p13: vacío superior eliminado.
- p3: «Vistas de detalle» deja de quedar huérfano al pie de columna.
- Escala unificada, o rotulada de forma explícita y consistente si no es posible (D-7).
- Códigos internos → nombres en castellano; el código, si es imprescindible, entre
  paréntesis: «Esmeralda–Paraguay», «tramo Lacroze–Libertador», «Villa Crespo (borde oeste)».
- Jerga C9 fuera de las páginas públicas (resuelto de raíz por B2 + B3).
- Firma huérfana de R05 y R07: eliminada.
- «INFORMEFINAL» y «EPSG:5347» fuera de las páginas; van al anexo.
- **Badge de cifra con clave visual** según `naturaleza`: exacta / cota inferior (≥) /
  antecedente histórico / sin cifra comparable, distinguibles a simple vista, con la clave
  explicada una vez en la p4 «Cómo leer».

**Aceptación:** inspección visual de las páginas afectadas; ningún rótulo cortado ni
superpuesto; una sola aparición del descargo por página.

---

### B5 — Contenido ejecutivo

**Toca:** `contenido/contenido_atlas_v2.json`, `scripts/build_atlas_v2.py`.

- **p2 reescrita** para abrir con datos de la Ciudad: cuántas referencias, dónde, cuáles
  concentran más oferta relevada, qué familias predominan. **Todos los números salen del
  corpus tal como están** (R10 907, R08 646, R09 327, R17 189, R15 119, R14 79, R11 66;
  cotas R12 ≥797, R21 ≥254, R18 ≥216, R19 ≥211, R22 ≥158, R13 ≥314, R20 ≥40; antecedentes
  R05 697, R06/R07 72). **No se suman entre sí ni se ordenan en un ranking general**; la
  advertencia de no-comparabilidad va al lado del dato, no en su lugar.
- **p5: 22 tipologías → 4–5 familias**, con la etiqueta fina como subtítulo de cada ficha.
  Propuesta de mapeo (D-4):

  | Familia | Referencias |
  |---|---|
  | Polo | R03, R04, R05, R06, R08, R13, R15 |
  | Polo con subzonas / multiparte | R01, R07, R10, R17 |
  | Eje o corredor | R02, R11, R14, R16, R19, R20 |
  | Área segmentada | R12 |
  | Referencia dispersa | R09, R18, R21, R22 |

- «Sin cifra canónica comparable» **baja de jerarquía**: pasa a línea secundaria en cuerpo
  normal («referencia caracterizada; sin conteo comparable»), con lo que sí se sabe arriba.
- **Fichas reescritas en positivo**: primero qué hay, después qué no se puede concluir.
  Todas las salvedades se mantienen; cambian el orden y el tono. (R01 hoy: once viñetas,
  siete empiezan con «no».)

**Aceptación:** la p2 abre con datos de la Ciudad; ninguna cifra alterada respecto del JSON
canónico (verificado por diff automático de cifras contra el contenido V1); ninguna ficha
abre con una negación; el mapa general usa los mismos colores de familia que la p5.

---

### B6 — QA visual real

**Toca:** `qa/` de la fase (nuevo), no el `qa/` del paquete V1.

Se preserva el QA automático que ya funciona (páginas, hashes, enlaces, privacidad,
metadatos, preservación de insumos) y se agrega lo que falta: **renderizar las 58 páginas y
mirarlas una por una**, completando `QA_VISUAL_INSPECCION_58.csv` con hallazgo real por
página. Sin filas en `PENDIENTE`.

**Controles obligatorios de cierre** (todos, sin excepción):
58 páginas exactas A4 sin páginas vacías · cero «DataGastro» · cero HDBSCAN, epsilon, ARI,
Jaccard, buffer heredado, businessStatus, NO_EVALUABLE, INFORMEFINAL, EPSG, proxy
reproducible, Z0x-Sx, C-S0x · cero «Convenciones comunes» / «Lectura y límites» / «Caveat
geométrico» · una sola aparición del descargo por página · cero caracteres mal codificados
(Ã, â, �) y tildes intactas («Cañitas», «García del Río», «Villa Pueyrredón»,
«gastronómico») · ningún rótulo tapado, cortado ni superpuesto en los 29 mapas · ninguna
referencia visualmente fusionada con otra que el corpus declara independiente · enlaces
internos y marcadores funcionando.

**Aceptación:** los 12 controles en PASS con evidencia; 58/58 filas con hallazgo real.

---

## Orden de ejecución y puntos de corte

```
B2 (geometría)  →  B4+B3 (página de mapa)  →  B1 (mapa general)  →  B5 (contenido)  →  B6 (QA)
```

B2 va primero porque B1 lo necesita y porque resuelve de raíz la mitad de B4 y todo C9.
**Después de cada bloque:** regenerar el PDF, renderizar las páginas afectadas a PNG,
mirarlas, y reportarte qué cambió **antes** de seguir. Sin encadenar bloques.

---

## Riesgos

| # | Riesgo | Mitigación |
|---|---|---|
| R-1 | **Redibujar cambia la lectura territorial.** Un buffer generoso puede sugerir extensión donde el corpus dijo «tramo modesto» (R20) o «sin corredor demostrado» (R13). | Buffer conservador por defecto (D-1) + recorte Voronoi + la línea «Qué no es» de B3 en cada página. Ante duda concreta, freno y pregunto. |
| R-2 | **H-1: ocho referencias sin puntos.** No se puede re-envolver lo que no se observó. | Camino B (suavizado de la geometría cerrada). Documentado ficha por ficha en `CAMBIOS_V2.md`. |
| R-3 | **R18 seguirá siendo circular** (D-5a). Su texto dice «sin núcleo radial demostrado». | Se resuelve por rótulo, no por dibujo: se etiqueta como radio de consulta de 400 m y se quita el punto central. Inventar un contorno sería violar la regla 2. |
| R-4 | **Densificar Voronoi es caro** con 22 geometrías complejas. | Densificado adaptativo + cacheo del resultado en `capas/`; la corrida es offline y se ejecuta una vez. |
| R-5 | **Perder los enlaces internos y los 47 marcadores** al reescribir el layout. | B6 los verifica explícitamente; el generador V1 ya los emite y se conserva ese código. |
| R-6 | **Regresión de QA automático** al derivar el generador. | Se copia el generador y se conservan `validate_inputs()`, `privacy_qa()`, `preservation_qa()` sin tocar. |
| R-7 | **R16 tiene 9 puntos propios** y 125 compartidos con R17. Un envolvente sobre 9 puntos es frágil. | R16 va por Camino B (su doble eje con buffer 200 m ya está cerrado); los puntos compartidos **no** se reparten. |
| R-8 | **El callejero cambió de ruta** (H-3). | Apuntar a `outputs/polos_gastro/FASE5-29/fase15_mapas_callejeros_v3/assets/` y fijar su SHA-256 en el generador nuevo. |
| R-9 | Presión a «mejorar» una cifra al reescribir en positivo (B5). | Diff automático de cifras V1↔V2 como control de cierre; cualquier diferencia es FAIL. |

---

## Decisiones que necesito que tomes

**D-1 · Ancho de buffer por defecto y excepciones.**
Propongo **200 m** por defecto (Camino A), con estas excepciones alineadas a lo que el
corpus ya usó, para no contradecir su propia construcción: R11 Boulevard Caseros **120 m**
(tramo corto, 66 registros — 200 m se comería medio Barracas y el corpus dice «No extender
a Patricios o Barracas»); R10 Caballito **150 m** (907 puntos muy dispersos en 6,8 km²);
R16 y R19 **conservan sus 200 m / 250 m** originales. ¿Confirmás 200 m con estas cuatro
excepciones, o preferís otro número?

**D-2 · Vectorial completo o raster de fondo.**
**Recomiendo vectorial completo.** Verifiqué que reportlab 5.0.0 dibuja paths nativos y que
las 22 geometrías están disponibles: no hace falta raster para nada. Beneficio: el texto de
los mapas pasa a ser texto real, buscable y no pixelado, y **B6 pasa a poder auditarlo de
verdad** (hoy no puede — ver H-2). Costo: reescribir el renderer de la página de mapa. La
alternativa (raster de fondo + texto encima) deja el problema a medias.

**D-3 · El mapa general reemplaza la p6 o se agrega.**
Tu enunciado dice reemplazo y **coincido**: la hoja de contactos no aporta nada que el mapa
general no dé mejor. Se mantienen 58 páginas exactas y no se toca el `EXPECTED_PAGES = 58`
que el generador valida. Confirmame que reemplaza.

**D-4 · Colores de las familias.** Propuesta sobre la paleta institucional ya en uso
(`COLORS` del generador), verificando contraste sobre el gris de comunas:

| Familia | Color | Hex |
|---|---|---|
| Polo | azul institucional | `#1F3B57` |
| Polo con subzonas / multiparte | celeste | `#2C7FB8` |
| Eje o corredor | cobre | `#C0762B` |
| Área segmentada | verde | `#2D7A68` |
| Referencia dispersa | violeta apagado | `#7353A6` |

**D-5 · Tensiones entre el re-dibujo y el corpus.** Cuatro casos concretos:

- **D-5a · R18 Esmeralda–Paraguay.** Pedís que deje de ser un círculo perfecto tomando la
  envolvente de los puntos observados. **No es posible sin inventar**: su universo está
  hasheado, no hay puntos, y su geometría *es* un disco de 400 m por construcción
  (`nodo ESMERALDA x PARAGUAY radio=400.0`). Recomiendo mantener el disco, quitarle el
  punto central y rotularlo «área de consulta de 400 m en torno a Esmeralda y Paraguay», lo
  que **elimina la contradicción con «sin núcleo radial demostrado»** sin dibujar una forma
  que nadie midió. Alternativa si preferís: no publicar forma y mostrar solo la
  intersección rotulada. Necesito tu decisión.
- **D-5b · R22 Villa Pueyrredón.** Su geometría es el **límite barrial oficial** usado solo
  como marco de muestreo (`MARCO_MUESTREO_PROVISIONAL_NO_PRODUCTO_TERRITORIAL`). Suavizarlo
  lo convierte en algo que parece un área gastronómica y ya no es el límite barrial.
  Recomiendo dibujarlo **sin suavizar**, con trazo punteado y rótulo «marco de relevamiento,
  no área gastronómica». Sacar la grilla interna, eso sí.
- **D-5c · R20 García del Río.** Banda plana de 180 m con extremos rectos deliberados («no
  prolonga el eje antes de Cabildo ni dentro del parque»). El suavizado redondearía justo
  esos extremos. Recomiendo suavizar los lados y **preservar los extremos planos**.
- **D-5d · R09 Chacarita y R14 Boedo.** Sus cifras (327, 79) corresponden a recortes más
  chicos que el conjunto de puntos de la zona (Z02, Z07 con 271). Envolver todos los puntos
  daría un área visualmente mayor que la cifra que la acompaña. Recomiendo envolver solo los
  puntos dentro de la geometría de producto ya cerrada, y decirlo en «Qué mide la cifra».

**D-6 · Comunas en el resumen ejecutivo.** Para escribir «las referencias se distribuyen en
N comunas» habría que intersecar las geometrías con `geo_comunas.geojson`. Es un cruce de
ubicación, no un recálculo de universos, pero **produce un dato que hoy no está en el
corpus**. ¿Lo autorizás, o el resumen se queda con los nombres de barrio que ya figuran en
las fichas?

**D-7 · Escala.** Las 22 referencias van de 0,3 km² a 6,8 km²: una escala única deja R11 y
R20 ilegibles. Recomiendo **dos escalas normalizadas** (250 m para las compactas, 500 m para
las extensas), con la barra de escala siempre rotulada y una nota fija en la leyenda. La
alternativa —escala única— sacrifica legibilidad en cinco referencias.

**D-8 · Nombre y estado del entregable.** El PDF sale como
`ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_V2.pdf` en `outputs/polos_gastro/ATLAS_V2/`, y
el V1 institucional queda intacto. ¿Confirmás que esta fase **no** actualiza
`ESTADO_GENERAL_INFORMEFINAL.md` ni los marcadores globales, y que eso queda para una
decisión tuya posterior?

---

## Lo que esta fase NO hace

No recalcula ninguna cifra, universo, cota, proporción, saturación ni decisión territorial ·
no suma cifras entre referencias ni construye ranking general · no dice «locales activos» ·
no presenta las áreas como límites oficiales, padrón ni recomendación comercial · no usa red,
geocodificación nueva ni APIs pagas · no escribe «DataGastro» en el PDF ni en los assets ·
no modifica los PNG ni ningún insumo de `cartografia_22_correccion_visual_v1/` ni de los
paquetes congelados · no expone datos personales · no borra ni mueve archivos del proyecto
sin plan de limpieza previo y confirmación tuya.
