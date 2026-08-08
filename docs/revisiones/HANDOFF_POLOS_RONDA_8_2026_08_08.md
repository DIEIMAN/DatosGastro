# HANDOFF · Ronda 8 · Places contestó, y lo que dijo es sobre Places · 2026-08-08

Continúa `HANDOFF_POLOS_RONDA_7_2026_08_08.md`. Rama `mercados-gastronomicos-v2`.
**Google Places: 71 requests.** Primera corrida paga del barrido desde el 06/08.

**Tres scripts nuevos** y uno parametrizado:

1. `scripts/barrido_ciudad/ronda_8_places_incremental.py` → `places_cola_r8.csv`,
   `places_resultado_r8.csv`, `places_tests_calibracion_r8.csv`, `PLACES_R8.txt`, y el crudo en
   `outputs/analisis_interno/places_vigencia_2026-08/` (Git lo ignora)
2. `scripts/barrido_ciudad/ronda_8_hitos_y_fuentes.py` → `hitos_capa_2026_r8.csv` (225 hitos,
   38 columnas), `cambios_ronda_8.csv`, `RONDA_8_HITOS.txt`, `anclajes_normativos_r8.csv`
3. `scripts/barrido_ciudad/ronda_8_geometria.py` → `geometria_r8/referencias_r8.geojson`,
   `fusion_chacagiales_r8.csv`, `solapes_r8.csv`, `cola_de_R20_declarada.csv`, `GEOMETRIA_R8.txt`
4. `ronda_7_familias_de_vias.py` ahora acepta `--capa`, `--referencias`, `--sufijo` y `--remapeo`.
   El default sigue siendo la ronda 7 y reproduce sus salidas idénticas.

---

## Lo más importante de la corrida: los cinco tests

| establecimiento | lo que sabemos | días | Places dice | |
|---|---|---|---|---|
| Plaza Bar | cerrado desde abril de 2017 | 3.285 | `CLOSED_PERMANENTLY` | **acierta** |
| La Buena Medida | cerrada desde octubre de 2025 | 280 | `OPERATIONAL` | **falla** |
| The New Brighton | quiebra declarada el 18/03/2026 | 143 | `OPERATIONAL` | **falla** |
| El Tokio | cerró 2023, reabrió 2025 | — | `OPERATIONAL` | acierta |
| Los Laureles | cerró julio 2026, ya reabrió | — | `OPERATIONAL` | acierta |

**De tres cierres conocidos, Places marca uno.** El piso de detección está **por encima de los 280
días**: hay un cierre de nueve meses, y otro con quiebra declarada por la Justicia hace cinco, que
Places sigue dando operativos.

Los dos tests de reapertura sí pasan: Places no arrastra cierres viejos de locales que volvieron.

### Lo que eso le hace a la escala

`PLACES_PARA_VIGENCIA.md` sostenía que «Places es bueno con la decadencia lenta» y ponía al Plaza
Bar como caso. **Eso se confirma, pero el umbral es mucho peor de lo que la nota suponía.** La
frase que hay que corregir es la que decía que Places cubre el punto ciego de la prensa: lo cubre
recién arriba de los nueve meses.

> **v2b acredita cierre cuando Places lo afirma, y NO acredita apertura ni descarta cierre cuando
> calla.** Un `OPERATIONAL` de Places es compatible con un local cerrado hace nueve meses.

Hay que escribirlo en la escala **antes** de que alguien lea los 70 `OPERATIONAL` de esta corrida
como 70 confirmaciones. No son ninguna confirmación.

**Candidato a FD-20, no cargado porque no estaba pedido:** el `OPERATIONAL` de Places sobre un
local con quiebra judicial declarada es un falso negativo de la misma familia que FD-12, sólo que
en el sentido contrario. Queda a decisión de Diego.

---

## Consumo y corte

| | |
|---|---|
| requests gastados | **71 de 71** |
| dónde se cortó | **no se cortó** — la cola entró completa |
| costo si el cupo Enterprise estaba libre | **USD 0,00** (71 ≤ 1.000 gratis/mes) |
| costo si el cupo ya estaba agotado | USD 2,48 |

**El precio, verificado antes del primer request** contra
`developers.google.com/maps/billing-and-pricing/pricing`: Text Search **Enterprise**, 1.000
llamadas gratis por mes y **USD 35,00 por 1.000** después. **No es la consola de facturación de
Diego** —este proceso no puede leerla— y por eso la corrida llevó tope duro y corte al primer error.

**La corrida cae en Enterprise y no por elección:** `places.regularOpeningHours` es campo
Enterprise y se factura al SKU más alto que toque la máscara. Los tres campos los fijó la decisión
4. Las corridas de Places de agosto de este repositorio usan una máscara **sin** ese campo, así que
consumieron Pro y no el cupo Enterprise; lo esperable es USD 0,00. Cuál de los dos fue, sólo lo
dice la consola.

La caché se escribe **después de cada request**, así que un corte no habría perdido nada. Volver a
correr el guion hoy gasta 0.

---

## El control de identidad, que casi da un falso positivo

De las 71, **60 devolvieron la dirección exacta** y **10 la misma calle a menos de 30 números** —
numeración de fachada, ochava o portal contiguo: El Tokio 3550/3548, Casa Watson 2072/2070, La
Perla 1899/1895. Se dan por buenas.

**Una no:** `Crizia` — consultada en Gorriti 5143, Places devolvió **Fitz Roy 1819**, otra calle.
Su estado **no se atribuye** al establecimiento y queda anotado en la capa.

El primer control que escribí contaba las 11 juntas como fallas. Distinguir «otra cuadra» de «otra
calle» convirtió once alarmas en una.

---

## Lo que Places cambió en la capa: nada

70 `OPERATIONAL` y 1 `CLOSED_PERMANENTLY`, y el único cerrado —Plaza Bar— ya estaba cerrado en la
capa desde antes. **Ningún veredicto se movió.** No es que la corrida fallara: la asimetría estaba
declarada de antemano y un `OPERATIONAL` nunca iba a subir a nadie.

Lo que sí se escribió en los 70: `places_business_status` y `vigencia_fecha_consulta`. Places no
trae la fecha del dato; sin esa columna, en seis meses tendríamos un campo sin saber de cuándo es,
que es FD-01 aplicado a otra fuente.

**Lo que la corrida produjo es la medición de Places, que es lo que se compró.**

---

## Los cinco veredictos de la tanda A, aplicados

| hito | | nivel | dato del |
|---|---|---|---|
| H009 Bar El Federal | `si` | v3 | 21/07/2026 |
| H074 Los 36 Billares | `si` | v3 | 04/07/2026 |
| H035 Café Tortoni | `si` | v3 | 26/05/2026 |
| H024 Café de los Angelitos | `si` | v3 | 25/05/2026 |
| H085 Varela Varelita | `si` | v3 | 25/06/2026 |

**La vía B por zona sube de 33 a 39 de 94**, y por contención de 16 a 19. Monserrat pasa a tener
tres verificados.

---

## El nudo Chacagiales, fusionado

| | ha | locales | morfología del clustering |
|---|---|---|---|
| R09 Chacarita | 94,8 | 202 | «dispersa» |
| R19 Federico Lacroze (ampliada en r7) | 303,3 | 532 | «eje» |
| Z43 Colegiales (barrio) | 229,1 | 441 | — |
| **R09 ∪ R19** | **337,7** | **581** | |
| **el polo fusionado, con Colegiales** | **495,8** | **891** | **sistema de subpolos** |

`R09 ∩ R19` valía **60,4 ha, el 64 % de Chacarita**, y desaparece: los dos son ahora el mismo
objeto. Contención verificada: **0,0 m² perdidos** de cada uno de los dos publicados.

**Colegiales entra a escala de barrio, y eso es un techo, no una medición.** Z43 no tiene perímetro
delimitado; hasta que se construya, el barrio es lo más chico que se puede usar sin inventar. La
diferencia —**158,1 ha y 310 locales**— es lo que está en juego y conviene decidirlo.

**Z44 Villa Ortúzar queda afuera, medido:** sólo el **3,6 %** del barrio cae dentro del polo
fusionado. Es contigüidad de borde, no pertenencia.

### Los otros cinco solapes

| | r7 | r8 |
|---|---|---|
| R08 ∩ R21 | 49,68 ha | **49,68 ha** — sin tocar |
| R02 ∩ R12 | 21,72 ha | 21,72 ha — venía de antes |
| R01 ∩ Chacagiales | 3,32 ha | **9,90 ha** — creció con Colegiales |
| R08 ∩ Chacagiales | 7,78 ha | 7,78 ha |
| Chacagiales ∩ R21 | 7,25 / 2,25 ha | **7,52 ha** — las dos parejas colapsan en una |

La fusión resuelve el más grande y **no toca los demás**: la precedencia sigue siendo editorial.

---

## Las tres correcciones

**Z23 Flores casco histórico** ya tiene perímetro construible: Av. Rivadavia entre Carabobo/Boyacá
y **Av. Nazca**, 1.270 m de eje, **45,2 ha y 154 locales**, con ensanche en Plaza Flores —que en la
capa oficial de espacios verdes se llama **PLAZA PUEYRREDÓN**, 0,68 ha, verificada por posición a
21 m del eje y no adjudicada por nombre—. **El veredicto no cambia: sigue PENDIENTE.** Medido: La
Farmacia queda a **405 m afuera** del perímetro corregido.

**Yiyo el Zeneize (H199)** retipado de `Mercado/patio` a `Restaurante/bodegón`, con
`registro_oficial = ley_especifica`: la Ley CABA 6.533 declara patrimonio su **carta
gastronómica**, no el local como mercado. **La fila que se mueve es una:
`PGR_P004 · Villa Lugano`, que pierde la vía C.** Es la misma regla que la decisión 1 aplicó a la
FIAB.

**La cola de R20**, declarada: de las 61,0 ha del polígono, **24,8 ha (41 % de la superficie y
53 % de los locales)** quedan fuera del tramo Cabildo–Balbín. Se conservan por contención y el
texto para la ficha está en `cola_de_R20_declarada.csv`.

---

## Barracas · tres objetos, cero altas

Cruzado contra la capa **antes** de dar de alta nada, que es la regla:

- **El Puentecito ya estaba** como `ICO-004`. **No cerró:** la alarma era una atribución
  equivocada; la pieza que la zona perdió es Los Laureles, a 1,5 km. → `probablemente_abierto` v4.
  En la ficha van **dos cifras con su fuente y su objeto**: 1750 el SITIO (pulpería y posta, dato
  del GCBA sin respaldo en prensa) y ~1876 el ESTABLECIMIENTO.
- **Los Campeones ya estaba** como `DIR-014`, ya tipado pizzería y con `pizzeria_emblematica`. Se
  actualiza a `probablemente_abierto` v5 con la camada de mayo de 2026 verificada contra
  **apyce.org**, el organizador. Fundada en 1954.
- **El CCCA de Av. Montes de Oca no es un hito**: va a `anclajes_normativos_r8.csv` como **figura
  ADMINISTRATIVA de obra pública, no legislada** — Resolución 65/SSADMIN/2017, Licitación
  1242/SIGAF/2017, BO CABA 5206 pág. 239, $28.054.630,31. **No existe ley que cree la figura CCCA**
  y eso queda escrito en el propio registro. Es el anclaje que le faltaba a Barracas · Montes de
  Oca.

---

## Cuatro trampas nuevas, y una que no es de fuente

La capa de fuentes con defecto pasa de **5 a 9**. Las cuatro son sobre el **canal**, no sobre el
documento ni sobre el establecimiento:

- **FD-16** · dato normativo que sólo sobrevive en el **slug** de una URL. La lectura de slugs
  entra como ruta de rescate, señalada siempre como tal: es haber leído cómo alguien tituló la
  página, no la página.
- **FD-17** · `cronista.com` **fabrica antigüedades** (150 y 200 años para el mismo local). Además
  de re-sellar fechas, que ya era FD-01.
- **FD-18** · **reetiquetado editorial**: «salón de la fama porteño» por Pizzerías Emblemáticas de
  APyCE. Copiar la etiqueta registra en el Atlas una institución inexistente que suena a padrón.
- **FD-19** · fichas del GCBA **vivas y momias con el mismo tono**: una editada el 20/02/2026 y
  otra inerte desde el 08/09/2021, indistinguibles por el texto. Fechar una por una.

**Y la nota de GEOS, en la edición técnica junto a las trampas de fuente:** `covers()` devuelve
`False` sobre geometrías cuya diferencia mide exactamente 0,0 m². Va ahí por el mismo motivo que
las otras: **falla sin tirar ningún error**, y las dos formas de equivocarse —abortar una corrida
correcta o dar por buena una que pierde superficie— están disponibles y ninguna avisa.

---

## Lo que espera decisión

1. **Corregir la escala de vigencia** con el piso de detección medido: v2b no descarta cierre.
2. **Colegiales dentro de Chacagiales entra a escala de barrio**: 158,1 ha y 310 locales de
   diferencia contra el núcleo R09 ∪ R19. Delimitar Z43 o aceptar el techo.
3. **R08 ∩ R21 = 49,7 ha** sigue abierto, y ahora es el mayor.
4. **Crizia**: Places devolvió otra calle. Revisar a mano si se mudó.
5. **FD-20 candidato**: el falso negativo de Places sobre una quiebra declarada.
6. **Villa Lugano pierde su vía C** con el retipado de Yiyo: revisar si la fila sigue entrando.
7. Siguen de antes los pendientes de las rondas 3 a 7.
