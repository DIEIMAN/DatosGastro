# HANDOFF · Barrido de la Ciudad y comparabilidad de métodos · 2026-08-05

Continúa el trabajo abierto por `outputs/BARRIDO_CIUDAD_2026-08/` (base documental, búsqueda de
fuentes, crosswalk y spec de Places, hechos por Diego fuera del repositorio). Rama:
`mercados-gastronomicos-v2`. Sin commit.

## Estado

| paso | estado |
|---|---|
| Portar la capa homogénea al repositorio | **hecho y validado** (igualdad exacta con `--check`) |
| Relevamiento de Usos del Suelo · dos controles | **hecho**: entra como fuente primaria |
| MOC | **hecho**: exporta crudo, pero no resuelve vigencia (serie hasta 2017, `NIVEL` ordinal) |
| Las tres decisiones de Diego (primera tanda) | **aplicadas** |
| 22 zonas recalculadas contra el Relevamiento + añadas | **hecho** |
| Detector de lotes de permisos | **hecho**: 45 lotes, 22,6 % del padrón |
| **Prueba del SMP sobre los lotes** | **hecha, con la línea de base corregida** (ver abajo) |
| **Consulta técnica a la AGC** | **redactada y reordenada.** Falta que **Diego** la mande |
| Fichas documentales del oeste y del sur | **hechas y actualizadas**: 20 fichas con el aviso de trámites |
| Aviso de la columna `habilitaciones` | **propagado** a fichas, tablas y diccionario de columnas |
| Google Places · control de 17 zonas | **CORRIDO el 2026-08-05: 256 requests de 301** (ver abajo) |
| Denominador del control de Places | **CORREGIDO**: el eje es `Places ÷ cifra publicada`, no `Places ÷ base` |
| Prueba de techo sobre R08 | **CORRIDA: 50 requests de 150. Del orden del 12 %; «barrida chica» descartada** |
| **Captura-recaptura entre las dos corridas** | **HECHA, 0 requests. N̂ ≈ 77: el universo alcanzable está casi agotado con una corrida** |
| **Cruce Places × base documental en R08** | **HECHO, 0 requests. El aporte de Places es descubrimiento, no vigencia** |
| **Estimador padrón × Places sobre las 17 zonas** | **PROBADO Y DESCARTADO, 0 requests.** Falla contra las cifras de campo |
| **Límite del detector de saturación** | **ANOTADO** en el informe de la prueba de techo. Frente de Places **CERRADO** |
| **Paquete de campo de Núñez y La Boca** | **HECHO**: piso, perímetro tentativo, banda de control |
| Plan del barrido de los 48 barrios | **DESCONGELADO Y CORREGIDO en una sola pasada** (spec §3, diseño de cuatro fuentes, aviso de la grilla). La grilla **no se recalculó**: decide Diego |

Informes: `outputs/BARRIDO_CIUDAD_2026-08/CONTROLES_FUENTES_NUEVAS_2026-08.md` (primera ronda) y
`APLICACION_DECISIONES_2026-08.md` (segunda ronda; supera las cifras del Relevamiento de la
primera).

## El código, y en qué orden se corre

```text
scripts/barrido_ciudad/
  build_capa_homogenea.py --check    # las tres tablas de referencia, con control de aceptación
  perfilar_usos_suelo.py             # controles del Relevamiento + capa por barrio
  capa_rus_por_zona.py               # las 22 zonas sobre el Relevamiento (necesita el SHP)
  detectar_lotes_permisos.py         # lotes de permisos replicados
  probar_smp_lotes.py                # la prueba catastral que cierra el caso de los lotes
  build_fichas_documentales.py       # las 20 fichas (corre después de los tres anteriores)
  preparar_consulta_agc.py           # la nota a la AGC y su anexo. NO envía nada
  documentar_columnas.py             # el diccionario que viaja con los CSV
  estimar_costo_places.py            # conteo de requests, sin red
  places_control_zonas.py            # el control de Places. Dry-run por defecto
  places_techo_zona.py               # la prueba de techo sobre una zona. Dry-run por defecto
  captura_recaptura_places.py        # el solape entre las dos corridas. NO toca la red, nunca
  cruzar_places_padron.py            # qué trae Places que la documental no tiene. Sin red
  universo_por_captura_recaptura.py  # el estimador padrón × Places, probado y descartado. Sin red
  preparar_campo_barrio.py           # el paquete de campo de Núñez y La Boca. Sin red
```

`places_techo_zona.py` importa de `places_control_zonas.py` la geometría, la precedencia de
envolventes, el dedup y la carga de la key en vez de duplicarlas: la regla de solape se pierde
justamente cuando se copia y pega.

Correr siempre con `.venv/Scripts/python.exe` y `PYTHONIOENCODING=utf-8`; la consola rompe los
acentos. `-W ignore` evita el ruido de avisos de CRS de geopandas.

## El control de Places, corrido

**No hacía falta ninguna key nueva: la key estaba en el `.env` del repositorio, pero ningún
script cargaba `.env` al entorno.** El abort era correcto y el motivo equivocado. Se agregó
`cargar_dotenv()` a `places_control_zonas.py` y a `google_places_piloto.py`: parser propio de
cinco líneas, sin `python-dotenv`, sin pisar lo que ya esté exportado y sin fallar si `.env` no
está. El guardarraíl se conserva —la key sigue leyéndose sólo del entorno, no entra por CLI, no
se imprime y no se escribe a disco.

```powershell
.venv\Scripts\python.exe scripts\barrido_ciudad\places_control_zonas.py            # dry-run
.venv\Scripts\python.exe scripts\barrido_ciudad\places_control_zonas.py --run --confirm-real-api
.venv\Scripts\python.exe scripts\barrido_ciudad\places_control_zonas.py --reinformar  # sin red
```

**Corrida del 2026-08-05: 256 requests gastados de 301 autorizados (−15 %).** El tope duro de 361
no se acercó. 95 celdas de 1 km, 23 repartidas en 500 m, 1.055 puntos devueltos.

### El denominador, corregido el 2026-08-05

**La primera versión de este informe comparó dos razones distintas y hay que no repetirlo.** Las
bandas de las 22 zonas son **base ÷ cifra publicada** (Villa Crespo: 233 ÷ 646 = 36,1 %). Lo que se
encabezó para Places era **Places ÷ base** (29 ÷ 100 = 29,0 % en Belgrano). Que 29,6 % cayera adentro
de 7,6–36,1 % era coincidencia aritmética, no equivalencia: son cantidades con distinto denominador.

Con el denominador común —el mismo que usan todos los demás métodos— el cuadro es **más neto**, no
menos. Places queda por debajo de toda fuente documental que ya tenemos, en las cuatro familias:

| cifra publicada obtenida por | padrón ÷ publicada | Relevamiento ÷ publicada | **Places ÷ publicada** |
|---|---|---|---|
| relevamiento propio (n=4) | 7,6 – 36,1 (med. 18,1) | 22,4 – 52,5 (med. 29,0) | **4,0 – 15,2 (med. 9,7)** |
| mínimo relevado (n=7) | 13,9 – 57,3 (med. 30,4) | 16,7 – 52,5 (med. 44,9) | **5,1 – 17,5 (med. 7,6)** |
| relevamiento anterior (n=2) | 4,2 – 14,3 (med. 9,2) | 19,1 (n=1) | **4,2 – 12,5 (med. 8,3)** |
| directorio comercial (n=4) | 80,0 – 116,8 (med. 92,6) | 106,9 – 139,5 (med. 114,5) | **12,5 – 47,1 (med. 23,5)** |

La cifra publicada es el 100 % por construcción: es el patrón, no una columna más. **Contra un
conteo de campo real, Places recupera el 9,7 % —la mitad de lo que ya recupera el padrón solo
(18,1 %).** Belgrano: 29 de 697, o sea 4,2 %. Centro: 108 de ≥797, 13,6 %. Boulevard Caseros: 10 de
66, 15,2 %. Places supera al padrón en 2 de 17 zonas, y son justamente las dos de padrón más chico.

**La conclusión sobrevive al número correcto y se endurece:** Places no sustituye el trabajo de
campo. Lo que cae es la frase «captura como el campo» — captura bastante menos, y en Belgrano menos
que el propio padrón. La columna `pct_places_sobre_padron` se conserva en el CSV porque contesta
**otra** pregunta —si Places ve locales que la fuente documental no tiene— y va rotulada como eso.

### Lo que esta corrida no puede decidir todavía

**Lo medido es el techo de esta barrida, no el techo de Places.** Dos causas producen el mismo
número y la corrida no las separa:

- **saturación admitida:** R05, R11 y R12 conservan una celda en su techo aún a 500 m, y el
  refinamiento se cortó en un nivel;
- **una sola familia de consulta** («restaurantes bares y cafés»), cuando la spec preveía tres.

Por eso los porcentajes de arriba son **cotas inferiores**, y por eso **el plan de los 48 barrios
queda congelado** hasta la prueba de techo sobre R08 (ver más abajo). Cambiar el plan sobre una
medición saturada es el error caro.

Las advertencias que viajan pegadas a la tabla, en la columna `advertencia`:

- **R05, R11 y R12 son cotas inferiores:** les quedó una celda saturada aún a 500 m.
- **R07 y R11 dan la razón invertida > 100 %** por base documental chica (3 y 5 direcciones). Eso
  afecta sólo a `pct_places_sobre_padron`; **en el eje comparable las dos zonas cuentan normal**,
  porque ahí el denominador es la cifra publicada (72 y 66), que no es chica.
- **`places_ampliado` va vacío, no en cero.** La consulta pide restaurantes, bares y cafés y nunca
  busca panaderías: el anillo ampliado **no se midió**. Un cero diría «no hay».

`--reinformar` rehace la presentación desde los datos guardados sin gastar un request. Se usó para
corregir el informe tres veces sin volver a llamar a la API — incluida esta corrección de
denominador. La lectura la **redacta el script desde los números**, con las bandas recalculadas
desde las familias presentes en la tabla: si mañana cambia la clasificación de una zona, la
conclusión se mueve con ella en vez de sobrevivirle.

## La prueba de techo · R08 Villa Crespo · CORRIDA el 2026-08-05

`scripts/barrido_ciudad/places_techo_zona.py`. Autorizada en 150 requests; **se gastaron 50**. El
refinamiento cerró solo: 4 celdas saturaron a 1 km, se partieron a 500 m y ninguna volvió a
saturar. Nunca hizo falta un tercer nivel.

| familia | requests | núcleo nuevos | acumulado | % de 646 |
|---|---:|---:|---:|---:|
| A · «restaurantes bares y cafés» (idéntica al control) | 34 | 63 | 63 | 9,8 |
| B · «parrilla pizzería y comida al paso» | 8 | +18 | 81 | 12,5 |
| C · «heladería» | 8 | +0 | 81 | 12,5 |

**Las familias suman poco: +28,6 % relativo, no un múltiplo.** C no aportó un solo local nuevo. Esa
comparación es interna —mismas celdas, mismo día, misma geometría— y no depende de reproducir el
control, así que es la parte más sólida del resultado.

**El control de aceptación difirió: 63 contra 76**, y las dos causas importan:

- **10 de los 86 puntos que el control atribuía a R08 los trajeron celdas de zonas vecinas**
  (R21=7, R09=3). La celda de 1 km se conserva si *toca* la envolvente, así que las vecinas barren
  territorio propio. Geométricamente esos puntos son de R08 y el `sjoin` hace bien en dárselos,
  pero esta prueba consulta sólo celdas de R08 y nunca podía llegar a 86. La línea comparable es
  **76**, no 86. Está resuelto en `baseline_del_control()`.
- **Los 13 restantes NO son ruido difuso de la fuente**, como decía la primera versión de esto.
  La captura-recaptura los localizó (ver más abajo): 3 salen de cuatro celdas de 500 m que la
  segunda corrida nunca consultó —diferencia de esfuerzo, no de fuente— y de los 11 que quedan
  en celdas idénticas, **8 salen de una sola celda**: `R08_0101` devolvió 58 en el control y 40 en
  la prueba, cayó bajo el umbral y por eso no se refinó. Las otras siete celdas de 1 km
  contestaron lo mismo dentro de ±2 resultados.
- **Y las dos corridas son del MISMO día**, no de días distintos: el 2026-08-05, con media hora
  entre una y otra (`fecha_consulta` idéntica en los dos ficheros internos; los archivos se
  escribieron 14:15 y 14:48). La frase «otro día» estuvo en la primera versión de este handoff y
  era falsa.

**Text Search rankea, no enumera** — y ahora se sabe con qué firma. Que una celda de R21 encuentre
locales de R08 que la celda de R08 no trajo, y que el mismo rectángulo dé menos en otra corrida,
siguen siendo el mismo fenómeno. Lo que cambia es la descripción: **no son «subconjuntos
distintos»; es una lista rankeada estable servida hasta una profundidad que varía.** Dentro de
`R08_0101`, los tres primeros cuartos del ranking volvieron al 95 % y el último cuarto al 0 %. Lo
que entra en el corte reaparece; lo que queda pasado el corte desaparece entero.

Por eso la formulación correcta no es «una fuente que no reproduce su propio número no sirve para
contar». Es más precisa y más incómoda: **la fuente reproduce lo que sirve, y lo que no sirve no
aparece nunca.** No sirve para contar porque tiene un techo, no porque sea errática.

### Veredicto, contra las bandas escritas antes

Medición directa: **12,5 %** → CONCLUSIÓN FIRME.

**El rango 12,5 – 17,1 % que estuvo acá se retiró, y es una corrección de método.** Ese 17,1 %
aplicaba el factor de familias medido en la prueba (×1,286) a la línea del control, que es **otra
corrida**. La prueba misma demostró que dos corridas difieren: multiplicar el factor de una por el
total de la otra es exactamente la operación que el propio hallazgo prohíbe. Está sacado del
informe y del código (`como_se_reporta()` reemplazó a `robustez()`).

**Se reporta como propiedad de la fuente, no como valor puntual:**

> «Una barrida de Places sobre R08 recupera del orden del 12 % de la cifra relevada a pie. Medido:
> 12,5 % con tres familias y 11,8 % con una sola. Entre corridas de la misma consulta la variación
> fue del 14 % a igual esfuerzo.»

Que las dos mediciones caigan a 0,8 pp una de otra pese al ruido es **evidencia adicional a favor**,
no en contra. La banda de conclusión firme se sostiene igual: ninguna lectura se acerca al 60 %.

`--reinformar` rehace todo esto desde los datos guardados sin gastar un request.

### La captura-recaptura, que cierra el caso · CERO requests

`scripts/barrido_ciudad/captura_recaptura_places.py`. Dos muestras independientes de la misma
población, ya pagadas: familia A del control sobre celdas propias de R08 (n1 = 76) y familia A de
la prueba de techo, misma consulta y mismas celdas (n2 = 63). **No cuesta un request: es un merge
por `place_id`.** Las bandas de lectura están escritas en el código antes de calcular m.

| | |
|---|---:|
| m · `place_id` en común | **62** |
| de la muestra 1 volvió a aparecer | 81,6 % |
| **locales que la 2.ª corrida agregó a la 1.ª** | **1** |
| unión observada | 77 |
| **N̂ · Chapman** | **77,2** · IC 95 % 77 – 78 |
| N̂ a igual esfuerzo (24 celdas comunes; n1 = 73) | 74,2 · IC 74 – 75 |

**N̂ ≈ 77 → banda «UNIVERSO ALCANZABLE CASI AGOTADO · conclusión cerrada».** Las dos puntas del IC
caen en la misma banda, y la variante a igual esfuerzo también. Una corrida entera de la misma
consulta agregó **un** local: acumular corridas no cambia el orden de magnitud, así que el 12 % es
**techo estructural de esta consulta sobre esta grilla**, no techo de esta barrida. La hipótesis
«Places es no reproducible y hay que usarlo por acumulación» **queda descartada con número**.

Las dos advertencias van pegadas al número a donde vaya:

1. **N̂ es cota inferior**, y no por el motivo habitual. La desigualdad de captura acá no es
   gradual sino un corte: fuera de `R08_0101` la recaptura fue del 93,3 % **sin pendiente por
   ranking** (87,5 / 100 / 100 / 87,5 por cuarto). Un local que queda pasado el corte en las dos
   corridas tiene probabilidad de captura **cero**, y la captura-recaptura no lo ve por
   construcción. Debajo de 77 puede haber una cola que ninguna cantidad de corridas iguales va a
   mostrar. Bajar el corte es refinar celdas —diseño de barrida—, no acumular.
2. **Estima el universo alcanzable por esta consulta, no el universo real.** Los 646 son un conteo
   de campo. N̂ no es una segunda estimación de esa cifra y no se mezcla con ella.

Sensibilidad, aparte y no comparable: con la unión de las tres familias como segunda muestra
(n2 = 81, m = 64) da N̂ ≈ 96, que es el universo alcanzable por el **protocolo de tres familias** —
otro protocolo, otra pregunta—. Sigue siendo ~15 % de 646, lejos del 60 %.

**Anotado para el diseño futuro, NO ejecutado:** la familia C (heladería) aportó **cero** locales
nuevos y la B aportó 18 sobre 63. Si algún día se corre el barrido, C se descarta y se ahorra un
tercio del costo de familias; B paga lo que cuesta. Está escrito en el encabezado de `FAMILIAS` en
`places_techo_zona.py`. **No se tocó la spec:** el plan de los 48 sigue congelado y se replantea de
una sola vez.

### Lo que quedó escrito y conviene no perder

Separa las dos lecturas que el control no distingue: «Places encuentra poco» y «nuestra consulta
buscó poco» dan el mismo porcentaje. Villa Crespo es la zona mejor calibrada (646 a pie, factor
documental 36,1 %) y **ninguna de sus celdas quedó saturada a 500 m** en el control, así que su
13,3 % no arrastra el defecto de R05/R11/R12: lo que le falta es profundidad de consulta.

Levanta las tres limitaciones: tres familias de consulta en vez de una, refinamiento **sin tope de
niveles** (piso geométrico 62,5 m, que se declara si se alcanza) y paginación completa —que ya era
completa: 3 páginas es el tope duro de Text Search y no hay una cuarta—.

| concepto | requests |
|---|---:|
| piso exacto: 8 celdas de 1 km × 3 familias, nada satura | **24** |
| familia A medida en el control sobre R08 (8 celdas, 5 saturaron → 20 de 500 m, 0 saturaron) | **39** |
| estimación si B y C se comportaran como A (cota alta: son consultas más angostas) | **117** |
| **tope duro pedido** · sin tolerancia, corta exacto | **150** |

Franja mensual 5.000; gastados 256; disponibles 4.744; quedarían 4.594.

**La lectura está escrita en el código antes de correr** (`LECTURA_PREVIA`), y el script imprime el
veredicto que le toque al número: 0–15 % → conclusión firme y el plan de los 48 se replantea;
15–60 % → rango intermedio, decide Diego; 60 % o más → la barrida era chica, el plan no se toca y
se corrige la profundidad de consulta.

Tres cosas que se decidieron al escribirlo y conviene no perder:

- **La familia A es idéntica a la del control**, y es el control de aceptación: si no reproduce los
  86 núcleo de R08, cambió la API, la geometría o el código, y comparar familias no vale.
- **Las familias van por turnos, no en una cola compartida.** Con cola única los refinamientos de A
  se encolan antes y un corte por presupuesto la deja con el doble de celdas que a C: el aporte
  marginal de B y C —lo único que la prueba mide— saldría subestimado por el orden de la cola y no
  por lo que hay en la calle. Se encontró con una prueba de humo, no en producción.
- **El tope corta antes de una consulta que pudiera pasarse**, no después. Una celda cuesta hasta 3
  requests, así que comprobar «ya gasté todo» dejaría exceder en dos. Se pierden dos de margen y a
  cambio el tope autorizado es literal.

## El frente de Places, CERRADO · qué ve, no cuánto ve

La captura-recaptura contestó **cuánto** (12 %, techo estructural). Faltaba **qué**, y de eso
dependía si el barrido de los 48 barrios valía los 2.100 requests.
`scripts/barrido_ciudad/cruzar_places_padron.py`, cero requests, contra Villa Crespo, que es la
zona mejor calibrada que hay:

| los 81 puntos núcleo de Places se reparten en | puntos | % |
|---|---:|---:|
| dirección que el padrón núcleo ya tiene | 27 | 33,3 |
| a menos de 25 m de una dirección núcleo, sin coincidir en dirección | 7 | 8,6 |
| dirección en el padrón, otro anillo | 0 | 0,0 |
| **parcela gastronómica del Relevamiento que el padrón no tiene** | **26** | **32,1** |
| **sin coincidencia en NINGUNA fuente documental** | **21** | **25,9** |

**El aporte de Places es descubrimiento, no vigencia.** Las dos mitades del resultado:

- **como sonda de vigencia sobre lo conocido, es floja:** confirma abiertas 26 de las 233
  direcciones núcleo del padrón, el 11,2 %. La formulación «dice cuáles de los que conoce siguen
  abiertos» hay que corregirla: casi no conoce los nuestros;
- **como descubrimiento, aporta:** dos tercios de lo que trae no están en el padrón núcleo, y un
  cuarto no está en ninguna documental. De los 21 sin coincidencia, 9 caen a menos de 10 m de una
  parcela gastronómica del Relevamiento —posible desplazamiento del punto de Google— y 8 a más de
  30 m de la más cercana, que es descubrimiento sólido.

El cruce es por dirección, no por local: misma calle —comparando conjuntos de palabras, porque una
fuente escribe `GALLARDO, ANGEL AV.` y la otra `Av. Ángel Gallardo`— y altura dentro de ±10. La
sensibilidad está medida y el resultado no depende del corte: a ±5 coinciden 20, a ±10 son 27, a
±30 son 41, y a ±30 ya se están dando por iguales manzanas distintas y veredas opuestas. **La
unidad es la dirección**, así que un negocio nuevo en una dirección que el padrón registró con
otro titular cuenta como coincidencia: el descubrimiento medido es un piso, no un techo.

### Replicado en 14 zonas, y de ahí sale un indicador nuevo

`universo_por_captura_recaptura.py` calcula lo mismo sobre las 17 zonas del control. **La
proporción de lo que Places trae que el padrón ya tiene va del 7,1 % (La Paternal) al 81,8 %
(Esmeralda–Paraguay), con mediana del 37,5 %; en 11 de 14 zonas la mayoría de lo que Places
encuentra no está en el padrón.** No es un estimador ni supone nada: es un cociente entre dos
conjuntos que están en disco.

Y esa variación es en sí misma un dato: **mide cuán al día está el padrón en cada zona.** Es el
primer indicador de frescura del padrón que tenemos y sale de datos ya pagados.

### Lo que se probó y NO funcionó, con su prueba escrita antes

En Villa Crespo el solape con el padrón (33,3 %) es casi exactamente el que daría el azar (36,1 %,
que es lo que el padrón cubre de la cifra de campo). Eso sugería usar **padrón × Places como
captura-recaptura** para estimar el universo de un barrio sin caminarlo: no haría falta que Places
fuera completo, sólo que fuera independiente.

**Se probó sobre las 17 zonas, con las predicciones escritas antes de calcular, y falla.** De las
tres zonas con conteo de campo y m suficiente, acierta en una (R08 = 1,09) y en las otras dos da
0,40 y 0,43: subestima a la mitad. La coincidencia de Villa Crespo era una coincidencia. Las dos
fuentes **no** son independientes en general —se solapan más de lo que daría el azar, o sea que
las dos ven a los mismos locales visibles—, y bajo captura desigual el estimador queda corto.
**La línea se cierra: no se vuelve a intentar sin una fuente nueva.** Está en
`generado/UNIVERSO_POR_CAPTURA_17_ZONAS.txt`, con la tabla completa por si alguien quiere
reabrirla.

Sin las predicciones escritas antes, este resultado se habría publicado como hallazgo. Es la
segunda vez en esta etapa que esa disciplina evita un error caro; la primera fue el rango
12,5–17,1 % que se retiró por mezclar corridas.

### El límite del detector, anotado y no perseguido

Está impreso en el informe de `places_techo_zona.py`, donde se afirma que el refinamiento cerró
solo: **el detector mira el tope de página, no el corte del ranking.** Como la profundidad servida
varía sola —58 y 40 en la misma celda sin tocar nunca el tope de 60—, «ninguna celda saturó» NO
equivale a «ninguna celda quedó truncada».

No se persigue, y la razón es una cota: en el peor caso imaginable —otra corrida que devolviera un
conjunto totalmente disjunto— la unión sería 154 sobre 646, un 24 %. Sigue sin acercarse a
reemplazar la caminata.

## Núñez y La Boca · preparado para salir a la calle

Los dos barrios que la Dirección quiere al nivel de Caballito y Villa Crespo **no salen como
fichas documentales**: se cuentan a pie. `preparar_campo_barrio.py` deja lo que hace falta para
salir, y no espera a nadie: `generado/PREPARACION_CAMPO_NUNEZ_LA_BOCA.md` y
`generado/corredores_campo_nunez_la_boca.csv`.

| | Núñez | La Boca |
|---|---:|---:|
| padrón · direcciones núcleo | 121 | 55 |
| Relevamiento · parcelas núcleo activas | 177 | 117 |
| calles del perímetro propuesto | 11 | 9 |
| **cuadras a caminar** | **101** | **44** |
| base del padrón dentro del perímetro | 79 | 34 |
| base del Relevamiento dentro del perímetro | 108 | 79 |

El perímetro sale como lista de calles con tramos de altura, no como polígono: es la unidad con la
que se camina. Cubre el 62,8 % de la base documental de Núñez y el 61,7 % de la de La Boca; lo que
queda afuera se declara para que ampliarlo sea decisión de la Dirección.

**La banda de control, que es lo que pidió Diego:** cuando vuelvan con su cifra `N`, el factor
`base ÷ N` tiene que caer en el rango medido en las cuatro zonas que sí se contaron a pie —7,6 a
36,1 % contra el padrón, 22,4 a 52,5 % contra el Relevamiento—. La banda es ancha a propósito:
caer adentro no valida el conteo, caer afuera obliga a revisar el perímetro, el criterio de rubro
o el conteo antes de publicar. Los dos controles de aceptación del paquete reproducen exacto la
capa homogénea y el conteo del Relevamiento.

## Decisiones vigentes, para no re-litigar

1. **Equivalencia de rubros por simetría con el padrón.** CERVECERIA y SUSHI en el núcleo,
   CONFITERIA en el ampliado. Núcleo de la Ciudad 9.108 parcelas; el ampliado no cambia (10.888).
2. **El oeste entra en esta tanda**, por base documental, sin factor de captura y declarando la
   añada. Cuando se corra Places, **empezar por el oeste** (nueve de doce barrios relevados en 2022).
3. **Habilitaciones = base del rango de control; Relevamiento = segunda columna.** El factor de
   captura no se reporta nunca sin decir contra qué base se calculó.
   - rango de relevamiento propio contra habilitaciones: **7,6 – 36,1 %** (mediana 18,2)
   - el mismo contra el Relevamiento: **22,4 – 52,5 %** (mediana 29,0)
4. **Places: control completo de las 17 zonas**, no la versión reducida a las cuatro relevadas a
   pie. Los 199 requests de diferencia son el 4 % de la franja y compran la curva de calibración.
5. **Grilla adaptativa: 1 km, y se reparte en 500 m toda celda que devuelva ≥ 50.** Ni fija en
   500 m (gasta de más) ni fija en 1 km (pierde locales en silencio donde la estimación falla).
   **Cuántas celdas hubo que repartir se informa por separado**: es información sobre dónde
   nuestro factor de captura estimado se queda corto.
6. **La consulta a la AGC va como consulta técnica, no como hallazgo**, con partida y dirección
   solamente, y **la manda Diego**, no el repositorio.

**Pendiente anotado, no ejecutar:** el mapeo `confiteria → Pastelería` del padrón es discutible.
Si se cambia, se cambia en habilitaciones y en el Relevamiento en la misma corrida y se recalcula
todo. Está escrito en el encabezado de `perfilar_usos_suelo.py`.

## El caso de los lotes: el mecanismo lo cierra, el catastro corrobora

`probar_smp_lotes.py` — salida en `generado/PRUEBA_SMP_LOTES.txt`.

**Lo que prueba el caso es el mecanismo, y es causal:** el campo `calles` admite varios números de
puerta en un mismo registro (`PUEYRREDON AV. 460;PUEYRREDON AV. 468`) — el 13,9 % de los registros
crudos, y 15.237 de 42.246 parcelas figuran con más de una puerta. El padrón asienta el frente
entero del inmueble; la exportación de 2025 lo aplana a un domicilio por fila y cada número del
frente pasa a comportarse como dirección independiente. Caso testigo: la parcela `1-32-2B` reúne
**75 números de puerta** sobre Florida, Córdoba, Viamonte y San Martín. Es una manzana completa.

**El cruce catastral corrobora, pero no parejo, y la línea de base global lo escondía.** El
99,26 % de las 39.751 partidas del crudo resuelve a una sola parcela, pero el 63,3 % de esas
partidas tiene **una sola dirección** y resuelve a una parcela por construcción. Contra esa base,
48 de 48 era lo esperable por azar. La base correcta es condicional a cuántas direcciones tiene la
partida, y excluyendo del estrato a las partidas del propio test:

| direcciones | partidas | base limpia (una parcela) | partidas del test |
|---|---|---|---|
| 1 | 25.163 | 99,93 % | 0 |
| 2 | 9.839 | 99,60 % | 20 |
| 3-5 | 4.020 | 98,35 % | 11 |
| 6-10 | 505 | 91,27 % | 1 |
| **11+** | **224** | **42,47 %** | **5** |

O sea: **donde el test vale es en los inmuebles grandes.** En el estrato de 11+ direcciones la
partida se reparte entre varias parcelas más de la mitad de las veces, y las 5 partidas nuestras
de ese grupo resuelven todas a una: eso sí distingue, y son justamente los inmuebles que generan
el grueso del fenómeno (las manzanas del centro, Liniers, Palermo). En las 20 partidas de dos
direcciones la base es 99,6 % y el resultado **no dice nada**. Acertar las 37 por azar: 76,1 %
con la base global, 0,97 % con la condicional.

Por eso **no se reporta «48 de 48» a secas**, ni acá ni en la nota a la AGC.

Conclusión, sin cambios: son inmuebles únicos cargados contra cada número de su frente de manzana,
no locales por puerta. Ninguna cifra publicada está afectada —la regla 3 ya los excluye—; lo que
cambia es que la consulta a la AGC pasa de «¿esto qué es?» a «esto es esto, ¿lo confirman?».

## Reglas reconstruidas que no estaban escritas

Si alguna se pierde, las tablas dejan de reproducirse:

1. **Superposición de envolventes.** R02 se solapa con R12, y R18 está contenido en R12 en un
   64 %. La superficie compartida queda para el `referencia_id` menor. Sin esto R12 da 370 en vez
   de 327 y R18 da 104 en vez de 30. **También la usa `places_control_zonas.py`**: sin ella el
   control mediría dos veces el mismo territorio.
2. **Barrio de F01.** El campo `barrio` del CSV crudo, validado contra el polígono: si el punto no
   cae dentro del barrio declarado, gana la geometría. El `barrio` de `dim_ubicacion` **no**
   reproduce la tabla (difiere en 16 celdas).
3. **Orden de los 48 barrios:** por `dir_nucleo` y, a igualdad, por `f01_locales`.
4. **El crosswalk de Diego está calculado sobre las envolventes crudas**, sin descontar el solape.
   Reproduce exacto así (22 de 22, desvío ≤ 0,1 pp). Para R12 y R18 la añada que corresponde
   declarar es la del perímetro con precedencia, no la del crosswalk: en R18 la diferencia es de
   27 pp y da vuelta el barrio dominante.

## Trampas encontradas, para no repetirlas

- **El CSV del Relevamiento viene con doble codificación** (`CAF├ë` por `CAFÉ`): bytes UTF-8
  leídos como CP437. Hay dos controles que cortan la corrida si reaparece
  (`verificar_codificacion`, `verificar_vocabulario`). **El SHP viene bien codificado**: el defecto
  es del CSV.
- **Los crudos de F02 de 2015 a 2024 son `latin-1` y separados por `;`**, con encabezados que
  cambian de caja entre cohortes (`seccion` hasta 2019, `Seccion` desde 2020). El de 2025 es
  `utf-8` separado por comas y tiene **otras columnas**: trae `domicilio` y `nropartidamatriz`,
  pero **no trae catastro**.
- **Las claves catastrales vienen multivaluadas.** Cuando un trámite abarca dos parcelas, los
  cuatro campos traen `;` adentro y **alineados posicionalmente** (`29;29` / `105 ;105` /
  `019 ;019A` / `341115;378814`). Hay que explotarlos juntos: cruzar la sección de uno con la
  parcela de otro da basura silenciosa. Es el 0,88 % de los registros.
- **La parcela es alfanumérica** (`016q`, `158C`, `005a`) y viene con relleno de ceros y espacios.
  Sin normalizar, `105 ` y `105` cuentan como dos manzanas distintas.
- **El `bbox` de pyogrio se interpreta en el CRS del dataset.** Pasarle grados contra un SHP en
  Gauss-Krüger devuelve cero features **sin error**. Por eso `capa_rus_por_zona.py` trabaja entero
  en el CRS nativo del SHP. Mismo motivo para centroides y áreas: en grados salen mal. La grilla
  de Places se construye en EPSG:5347 y recién se convierte a grados para la llamada.
- **No nombrar `area` a una columna de un GeoDataFrame.** `.area` es una propiedad de la geometría
  y gana sobre la columna; el denominador sale de los polígonos completos y los porcentajes quedan
  mudos pero equivocados.
- **`id_habilitacion` no es el número de expediente**, es una clave nuestra: no sirve para medir
  correlatividad. El expediente real **sí está** en los crudos de 2015-2024 (`numero_expediente` /
  `NumeroExp`), sin explotar todavía.
- **R07 · Costanera Norte tiene 1 parcela relevada en 38,5 ha.** Su cero no es un cero: es falta
  de cobertura de la fuente. Los umbrales están en `capa_rus_por_zona.py` con la separación
  observada (0,03 parcelas/ha contra 10,8 de la zona más floja; norma de la Ciudad 15,6).
  `places_control_zonas.py` deja su factor contra el Relevamiento **vacío** por eso.
- **El CSV crudo de F01** es `latin-1`, separado por `;`, decimales por coma, con `Boca` por
  `La Boca` y un `Nuñez` doble codificado.
- **`sjoin` renombra columnas** cuando la capa de puntos ya tiene una columna `nombre` — F01 la
  tiene, es el nombre del local.
- **La celda de la grilla no es la zona, y confundirlas infla el conteo.** Una celda se conserva
  si *toca* la envolvente, y a la API se le pide el rectángulo entero: para una zona angosta —un
  bulevar, una avenida por tramos— el rectángulo cubre muchísimo más territorio que la envolvente.
  Atribuir a la zona todo lo que trajo la celda daba **captura por encima del 100 %**. Hay que
  hacer punto en polígono contra los perímetros con precedencia (`asignar_por_geometria()`).
  **El 41,4 % de los puntos devueltos cayó fuera de toda envolvente**: R11 pasó de 78 a 10, R05 de
  96 a 29, R12 de 247 a 108. Sin esta corrección el control entero decía otra cosa.
- **`.env` no se carga solo.** La key estaba en `.env` y ningún script lo leía, así que abortaba
  por «falta la key» teniéndola. Lo resuelve `cargar_dotenv()`, que no pisa lo que ya esté
  exportado. Si aparece de nuevo en otro script, es el mismo bug.
- **Un cero que no es un cero, otra vez.** `places_ampliado` daba 0 en las 17 zonas y no es que no
  haya panaderías: la consulta nunca las pide. Va vacío. Mismo criterio que el cero de R07.
- **El umbral de saturación decide el refinamiento, y el refinamiento decide la cobertura.** Una
  celda que en otra corrida devuelve 40 en vez de 58 no cruza el umbral de 50, no se parte, y sus
  cuatro hijas de 500 m nunca se consultan: la zona pierde locales **sin que nada avise**, porque
  la celda no falló ni dio error. Pasó en `R08_0101` y explica 11 de las 14 pérdidas entre las dos
  corridas. Al comparar dos corridas hay que comparar los CONJUNTOS DE CELDAS primero, no los
  totales: si difieren, parte de la diferencia es de esfuerzo y no de la fuente.
- **No mezclar corridas.** Aplicar un factor medido en una corrida al total de otra parece
  robustez y es contaminación. Era el origen del rango 12,5 – 17,1 % que se retiró.
- **El Relevamiento se cuenta por parcela ACTIVA y `SMP` único.** Contar registros da de más —una
  parcela con dos usos gastronómicos aparece dos veces— y no filtrar `ESTADO` mete las inactivas.
  La primera versión del paquete de campo daba 128 para La Boca contra los 117 de la ficha por
  esas dos cosas. La definición canónica está en `perfilar_usos_suelo.capa_por_barrio()` y
  cualquier conteo nuevo tiene que reproducirla, no reinventarla.
- **Tres estados, no dos, cuando se cruza contra una fuente que puede no estar.** «El punto no cae
  en ninguna parcela gastronómica» y «el Relevamiento no se consultó» dan el mismo `None` si no se
  separan, y el segundo se leería como descubrimiento. Es el mismo error del cero de
  `places_ampliado` y volvió a aparecer en el cruce; el arreglo es declarar el estado, no
  inferirlo de la ausencia.
- **Una coincidencia con la teoría no es una confirmación.** El estimador padrón × Places acertó
  en Villa Crespo y falló en las otras dos zonas con conteo de campo. Lo que lo distinguió fue
  haber escrito las predicciones por familia de método **antes** de calcular; sin eso el acierto
  de una zona se publica como método.
- Las descargas crudas quedan fuera de Git por reglas al final de `.gitignore`. Las tablas
  derivadas se versionan.

## Privacidad

Los crudos de F02 traen `titulares`, `cuits` y `telefono`. **No se leen.** En
`detectar_lotes_permisos.py` y en `probar_smp_lotes.py` las columnas que se abren están declaradas
en una constante única, y el `usecols` de pandas se arma desde ahí: lo prohibido no entra en
memoria. De `razon_social` se informan únicamente conteos, nunca valores.

La nota a la AGC lleva **partida, catastro, dirección y conteos, y nada más**. El script tiene un
control que aborta si alguna columna prohibida se cuela en el anexo.

## Lo que espera decisión o acción de Diego

1. **Mandar la nota a la AGC** — `outputs/BARRIDO_CIUDAD_2026-08/consulta_agc/`. Revisarla antes.
2. **El número de R08 ya no es una decisión entre dos puntas.** El rango 12,5 – 17,1 % se retiró
   por método (mezclaba corridas) y la captura-recaptura cerró la pregunta de fondo: N̂ ≈ 77, una
   corrida agregó un solo local, el 12 % es techo estructural. Se reporta como propiedad de la
   fuente, con la redacción que está más arriba. **Lo que falta es la firma de Diego sobre esa
   redacción**, no elegir un valor.
   - Va junto con la otra corrección de encuadre: **el aporte de Places es descubrimiento, no
     vigencia**. Es un cambio sobre lo que se venía diciendo y conviene que quede firmado igual,
     porque de ahí cuelga para qué se corre el barrido.
3. **El plan de los 48 barrios se DESCONGELÓ y se corrigió en una sola pasada**, como estaba
   pedido: `SPEC_PLACES_BARRIDO.md` §3 (la redacción vieja «si captura como el directorio
   comercial» reemplazada por lo medido), `DISENO_CUATRO_FUENTES.md` (el papel de Places y el
   estado de los seis pasos) y `AVISO_GRILLA_48_BARRIOS.md`. **La grilla no se recalculó**: el CSV
   sigue intacto y rehacerlo es una decisión de gasto.

   **Lo que falta decidir es correr o no el barrido, y con qué grilla. La recomendación:**

   **Correrlo, en dos tandas y con el objetivo cambiado.** No como censo —eso está descartado— sino
   como fuente de descubrimiento, que es lo que la medición muestra que hace. Tres cosas cambian
   respecto del plan congelado:

   - **la familia C (heladería) se descarta** —aportó cero locales nuevos— y quedan A y B. Un
     tercio menos de costo por celda, medido, no estimado;
   - **el orden ya no es por universo esperado**, que era una cuenta de conteo. Conviene empezar
     por donde el padrón está más desactualizado, y eso ahora se mide con la proporción de solape;
   - **la densidad no se baja.** Refinar la celda es lo único que baja el corte del ranking: menos
     densidad es menos descubrimiento, no el mismo resultado más barato. Ésta es la corrección al
     supuesto de que «para muestrear vigencia no hace falta esa densidad» —el objetivo no resultó
     ser vigencia—.

   **Primera tanda sugerida: los 8 barrios del sur y el oeste con ficha documental y peor padrón**,
   dentro de la franja gratuita del mes, y medir el aporte real antes de comprometer el resto. Si
   la tanda rinde como Villa Crespo, el resto se corre; si rinde como Esmeralda–Paraguay, no vale
   la pena y se cierra con lo que hay. **Es la misma lógica que hizo barata a esta etapa entera:
   una medición chica antes de la decisión grande.**

   Contra qué se mide: la franja son 5.000 requests mensuales, van gastados 306, y el barrido
   completo se estimó en 2.100 con la grilla vieja de una familia.
4. **El mapeo `confiteria → Pastelería`**, si se resuelve, arrastra el recálculo de las dos bases.
5. **Las 20 fichas del oeste y del sur salen** (decidido). Núñez y La Boca **no**: van a campo, y
   su paquete de preparación está listo. Lo que espera a Diego ahí es pasarle el paquete a la
   Dirección, no producirlo.

**Pendientes agrupados al próximo recongelamiento — anotados, NO ejecutados.** La referencia
congelada de `build_capa_homogenea.py --check` se rompe una sola vez, así que ningún cambio
cosmético la justifica por sí solo. Cuando haya que recongelar por un motivo de fondo, estos dos
entran en esa misma corrida:

- **renombrar `habilitaciones` a `tramites` en los CSV.** DECIDIDO QUE NO SE HACE AHORA: el lector
  ya está protegido por `DICCIONARIO_COLUMNAS.md`, el aviso del encabezado y la daga por barrio.
  El nombre agrega claridad, no protección, y no vale el control de aceptación;
- **el mapeo `confiteria → Pastelería`**, si Diego lo resuelve.

Están escritos en el docstring de `comparar()` en `build_capa_homogenea.py` y en el encabezado de
`perfilar_usos_suelo.py`, que es donde los va a leer el que toque eso.

## Lo que no se tocó

Ninguna cifra publicada del Atlas. La edición técnica V2.1 sellada; las fichas del oeste y del sur
son un producto separado. Los seis insumos canónicos verificados por SHA-256 y las capas de
`capas/` (solo lectura). El pipeline público F01–F05. La referencia congelada de
`capa_homogenea_*.csv` en la raíz del barrido —`--check` sigue dando **reproduce la capa exacta**.

De Google Places se gastaron **306 requests en agosto**: 256 de los 301 autorizados para el control
de las 17 zonas, y 50 de los 150 autorizados para la prueba de techo. **La captura-recaptura no
gastó ninguno**, y no puede: no tiene endpoint. Franja mensual 5.000, disponibles 4.694. Los puntos
con nombre y dirección quedaron en `outputs/analisis_interno/` (fuera de Git); lo versionable es el
agregado por zona.

**Todo lo que se agregó después de la captura-recaptura costó cero requests**: el cruce contra la
base documental, el estimador probado y descartado, y el paquete de campo de Núñez y La Boca salen
de datos que ya estaban en disco. El total de agosto sigue siendo 306. Las tres carpetas internas
nuevas —`cruce_places_padron_2026-08`, `campo_barrios_2026-08` y las anteriores— caen bajo
`outputs/analisis_interno/`, ignorada por Git desde la línea 11 del `.gitignore`.

**Sin commit.** Rama `mercados-gastronomicos-v2`.
