# HANDOFF · Ronda 5 · el catálogo vigente cambia, dos cargas de auditoría y el número de Places · 2026-08-07

Continúa `HANDOFF_POLOS_RONDA_4_2026_08_07.md` (misma fecha). Rama `mercados-gastronomicos-v2`.
**Google Places: 0 requests.** USIG: 4 consultas nuevas, cacheadas. Cinco cargas de Diego sobre
tres tareas de datos (catálogo vigente, auditoría de cierres, cierre de vigencia ronda 2) más una
tarea de diseño (costo de Places) y dos ajustes finos. Geometría, agrupamientos, fichas y
cartografía: **no tocados**, como pedía la consigna.

**Script nuevo: `scripts/barrido_ciudad/ronda_5_catalogo_vigencia.py`.** Salida:
`hitos_capa_2026_r5.csv` (221 filas, +1 sobre r3), `cambios_ronda_5.csv` (93 cambios con motivo,
fila por fila), `RONDA_5.txt`.

---

## Lo primero, porque no lo pidió nadie y lo encontró el diff

**H032 "Café Roma" no era un segundo Café Roma: era Roma del Abasto, fusionada por accidente.**
El emparejamiento de listas (GCBA + Wikidata + Boletín) tomó "Roma del Abasto" como variante de
nombre de "Café Roma" —coincide el token "Roma"— y le asignó una dirección que no es de ninguno de
los dos («San Luis 3101») con las coordenadas de Café Roma (Olavarría 409) reasignadas. Roma del
Abasto (Anchorena 806, orden 86/90) es una **alta real de la Res. 1225/26 que Diego no había
señalado** en su lista de movimientos — la encontró el diff sistemático, no una lectura dirigida.
Separado: H032 ahora es Roma del Abasto con domicilio y geocodificación reales (Balvanera, Comuna
3 según USIG); Café Roma (H031, Olavarría 409) queda como estaba.

---

## TAREA 1 · el catálogo vigente cambia

El PDF de la Res. MCGC 1225/26 se **volvió a descargar de la URL oficial** y se comparó **byte a
byte (SHA-256)** contra el archivo que ya estaba en disco desde el 3/08 (que la ronda 3 había
hasheado sin saber todavía que era el vigente): **coinciden exactamente.**
`75481a8abb834409a774d43a8cac92e90657d0a253077f6727b4ff45b2c99704`, 145.453 bytes,
IF-2026-10314379-GCABA-DGPMYCH, firmado 26/02/2026. Registro completo en
`outputs/BARRIDO_CIUDAD_2026-08/hitos/PROCEDENCIA_CATALOGOS.csv`.

El diff sistemático contra los 90 que teníamos cargados (`catalogo_1225_26_diff.csv`, nuevo):

- **1 baja real:** La Esquina de Aníbal Troilo (confirma lo que Diego identificó).
- **2 altas reales:** Bar Iberia, orden 10/90 (confirma; reingresa 3758/24→1225/26), y **Roma del
  Abasto**, orden 86/90 (no señalada, ver arriba). Ambas agregadas — Bar Iberia como hito nuevo
  `H094`, sin geocodificar hasta esta ronda.
- **1 renombre confirmado:** Café Palacio → Museo Fotográfico Simik, mismo domicilio (Av.
  Federico Lacroze 3901). Exactamente lo que Diego señaló.
- **2 casos que Diego dio como altas y el diff no encuentra como cambio:** Confitería El Greco y
  Josephina's Café **ya estaban** en el catálogo cargado (citado como 3758/24) antes de este
  diff. Puede que la transcripción que citamos como "3758/24" ya incluyera estas altas antes de
  tiempo. Queda como discrepancia sin resolver entre la cita de fuente y el contenido real — no se
  fuerza una explicación.
- **6 variantes de nombre/formato que NO son movimiento** (mismo domicilio en ambas listas):
  Bar Olimpo/Café Olimpo, Watson's/Casa Watson, Bar El Federal/El Federal, Café Tabac/Cafetabac,
  Montecarlo Bar y Despensa/Café Montecarlo, Bar Portuario/El Portuario.
- **12 altas que dejan de ser "sólo prensa":** los hitos marcados `es_alta_2026_08_03` ahora citan
  `declaratoria_localizada` con el número de orden en el consolidado (ej. H010 Bar Conde → orden
  5/90).

**Un hallazgo sobre la calidad del documento oficial, de paso:** el anexo tiene al menos dos
inconsistencias internas entre barrio y comuna. Dice "LA ACADEMIA Montevideo 341 **San Nicolás.
Comuna 5**" — San Nicolás es Comuna 1, no 5 — y "ROMA del ABASTO Anchorena 806 **Balvanera.
Comuna 5**" — USIG ubica ese punto en Comuna 3. Se adoptó el barrio/comuna de USIG en ambos casos
(fuente administrativa del punto), documentando la discrepancia en vez de heredarla en silencio.

---

## TAREA 2 · la auditoría de 11 cierres

Aplicado a la capa: **Plaza Bar** → `cerrado_con_reapertura_anunciada` (2028, bar histórico
conservado); **La Buena Medida** y **The New Brighton** → `no` (bajas reales, catálogo
desactualizado); **Esquina Homero Manzi** → `en_riesgo`, revisar el **2026-11-05** (90 días);
**La Esquina de Aníbal Troilo** → `senalado_no_cerrado` (la baja del catálogo es indicio, no
prueba); **La Academia** → domicilio corregido a Montevideo 341 y barrio a **San Nicolás según
USIG** (no Balvanera, que era la atribución de la auditoría — ver el hallazgo de arriba);
**Clásica y Moderna** → barrio corregido a Recoleta, vigencia resuelta por reapertura; **Café
Thibon** → vigencia resuelta (cambio de gestión, precedente de continuidad).

Sin acción sobre la capa (documentados en la auditoría, no son hitos nuestros): Confitería del
Hotel Castelar (ya excluida, baja de 3758/24) y El Palacio de la Papa Frita (no figura en ningún
catálogo, 33/23, 3758/24 ni 1225/26 — el catálogo tampoco explica sus propias bajas).

---

## TAREA 3 · se cierra la vigencia ronda 2

Diez filas verificadas por Diego, aplicadas: **Florida Garden, Casa Watson (v3), Bar Don Juan,
Bar de Cao, La Farmacia** → `si`. **Los Laureles** → `si`, **revierte P008 Barracas**: la
distinción que queda escrita es que el sitio de Turismo de la Ciudad publica una ficha **editada
activamente** para describir la reapertura (horarios nuevos y específicos), y eso es evidencia —
distinto de un listado inerte que arrastra un dato viejo (caso Plaza Bar, nueve años). El hito
sigue frágil: el inmueble está en venta. **Confitería Saint Moritz y Bárbaro** → `dudosa` con
`vigencia_sentido_duda = probablemente_abierto` (campo nuevo, para no perder la dirección de la
duda). **Café Olimpo** → `estado_operativo_pendiente` (campo nuevo): el único de los diez que no
se pudo resolver, y el caso que por sí solo justifica correr Places.

**El Sol de Galicia NO es un hito de esta capa** (es churrería, no Bar Notable — no vive en
`hitos_capa_2026`). Su dirección corregida, Luis Viale 2867, se confirmó con USIG: **Villa Santa
Rita, Comuna 11**, consistente con la zona Z27 que cita la vigencia. Si algún otro archivo de vía
B lo cita con la dirección vieja (2881), queda pendiente de corregir ahí — no se rastreó esta
ronda.

**Campos nuevos en la capa:** `vigencia_nivel` (v2/v3/v4), `vigencia_sentido_duda`,
`vigencia_revisar_hasta`, `nota_ronda_5`. Los valores nuevos de `vigencia_verificada`
(`cerrado_con_reapertura_anunciada`, `en_riesgo`, `senalado_no_cerrado`,
`estado_operativo_pendiente`) son extensión del enum, no reemplazo — la capa ya lo había hecho
antes con `sin_hitos` y `en_disputa`.

---

## TAREA 4 · el número de Places, para que Diego decida

Agregado a `PLACES_PARA_VIGENCIA.md` (que ya traía el diseño — v2b, la asimetría de
`business_status`, Places para descartar / prensa para confirmar, fecha de consulta obligatoria —
sin el número). **0 requests ejecutados: esto es una estimación, no una corrida.**

La API cobra por el campo más caro que se pida: `opening_hours` es SKU "Preferred" y arrastra a
todo el pedido, aunque `business_status` y `formatted_address` sean baratos. **Con la salvedad
explícita de que el precio no está verificado en vivo contra la consola de Google Cloud de este
proyecto** (la lista pública cambia sin aviso, y puede haber crédito mensual o descuento), el
orden de magnitud es de **USD 0,017–0,032 por solicitud**:

| conjunto | hitos | costo estimado |
|---|---|---|
| tandas A+B (ronda 4, prioritarias) | 29 | USD 0,49–0,93 |
| capa completa | 220 | USD 3,74–7,04 |

Recomendación: correr primero el subconjunto de 29 (13 % del universo, toca el 50 % de las filas
con hitos); si mueve fichas de `dudoso`/`sin_verificar` a un estado con evidencia, se autoriza el
resto con el patrón probado.

---

## TAREA 5 · dos ajustes finos

**FD-01 en la vía E de R03 San Telmo, recontada.** El Cronista (2021, act. 2025) queda excluido
del conteo de grupos independientes por FD-01; quedan La Nación (02/04/2026) y Time Out
(16/06/2025) — los food tours acompañan pero no suman un tercer grupo. `via_E_n_grupos` pasa de 3
a 2 en `via_E_22_referencias.csv` y `via_E_94_filas.csv`. **La vía E de R03 sigue abierta, por el
mínimo** — y es la única vía abierta de la fila, así que este recuento decidía si R03 quedaba con
cero vías o con una.

**El corredor del Barrio Chino, corregido donde estaba escrito.** `REPARACION_ENCLAVES_Y_TRES_CORRECCIONES.md`
y `enclaves_E02_E07_reparados.csv` decían "perpendicular al eje histórico"; medido en ronda 4 es
**casi paralelo, 19,1°** — Arribeños corre al lado de las vías, no las cruza. Se reemplazó también
el argumento contra el radio de cuatro manzanas por el mejor: no es que "equivoca la forma" en
abstracto, es que **captura la misma cantidad de puertas (45 de 49) gastando 2,7 veces más
superficie** (81,7 ha contra 30,7).

---

## Archivos tocados esta ronda

- `outputs/BARRIDO_CIUDAD_2026-08/hitos/hitos_capa_2026_r5.csv` (nuevo, 221 filas)
- `outputs/BARRIDO_CIUDAD_2026-08/hitos/cambios_ronda_5.csv` (nuevo, 93 cambios con motivo)
- `outputs/BARRIDO_CIUDAD_2026-08/hitos/PROCEDENCIA_CATALOGOS.csv` (fila nueva de verificación)
- `outputs/BARRIDO_CIUDAD_2026-08/hitos/RONDA_5.txt` (nuevo)
- `outputs/BARRIDO_CIUDAD_2026-08/fuentes/descargas_ronda_5/RES_MCGC_1225_26_ANX.pdf` (nuevo)
- `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/catalogo_1225_26_diff.csv` (nuevo)
- `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/PLACES_PARA_VIGENCIA.md` (+número)
- `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/via_E_22_referencias.csv` (R03)
- `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/via_E_94_filas.csv` (PG004_SAN_TELMO)
- `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/REPARACION_ENCLAVES_Y_TRES_CORRECCIONES.md`
- `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/enclaves_E02_E07_reparados.csv`
- `scripts/barrido_ciudad/ronda_5_catalogo_vigencia.py` (nuevo)
- `dataset_bares_notables/_cache_usig.json`, `seis_vias/_cache_usig_datos_utiles.json` (+4 consultas)

---

## Lo que espera decisión

1. **Roma del Abasto (H032→corregido) y Bar Iberia (H094, nuevo):** confirmar que la separación
   del bug de fusión no dejó ningún archivo derivado (cruces, conteos) todavía citando la fila
   vieja "Café Roma / San Luis 3101" — no se auditaron todos los derivados de
   `hitos_capa_2026_r3.csv` esta ronda, sólo la capa madre.
2. **El Sol de Galicia** con la dirección corregida (Luis Viale 2867): si vive en algún archivo de
   vía B con la dirección vieja (2881), sigue sin corregir ahí.
3. **Discrepancia barrio/comuna del anexo 1225/26** (La Academia, Roma del Abasto): documentada,
   no elevada como fuente con defecto formal (FD-02). Si se repite en más filas, conviene
   registrarla como tal.
4. **El Greco y Josephina's Café:** ya estaban en el catálogo citado como 3758/24 antes de este
   diff, contra lo que Diego había identificado como altas de 1225/26. Sin resolver por qué.
5. **Autorización de Places** para el subconjunto de 29 (tandas A+B), con el número ya estimado.
6. Sigue de antes: los puntos abiertos de ronda 3 y 4 que esta ronda no tocó (E02 forma final, los
   4 "afuera" del Barrio Chino, Ultramarinos sin geocodificar, R18, los 4 de la ronda 3 que
   faltaban decisión).
