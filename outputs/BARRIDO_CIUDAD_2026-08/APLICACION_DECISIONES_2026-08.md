# Aplicación de las tres decisiones y segundo rango calibrado

**Fecha:** 5 de agosto de 2026
**Continúa:** `CONTROLES_FUENTES_NUEVAS_2026-08.md`, cuyas cifras del Relevamiento quedan
superadas por la decisión 1 (ver §1).
**No incluye:** ninguna llamada a Google Places. El conteo de requests está estimado y sin
ejecutar, en §6.

---

## 1 · Las tres decisiones, aplicadas

### Decisión 1 · Equivalencia de rubros por simetría con el padrón

Verificada contra `fact_habilitacion_gastronomica.csv` antes de aplicarla, y coincide exacto con
lo indicado:

| valor de `TIPO2` | equivalente en el padrón | categoría | anillo |
|---|---|---|---|
| CERVECERIA | `despacho de bebidas,wisqueria, cerveceria` (5.571 hab.) | Bar | **núcleo** |
| SUSHI | sin rubro propio; cae en `restaurante, cantina` (4.401 hab.) | Restaurante | **núcleo** |
| CONFITERIA | `confiteria` (1.721 hab.) | Pastelería | **ampliado** |

Efecto sobre la Ciudad: el núcleo del Relevamiento pasa de 9.440 a **9.108 parcelas activas**
(entran CERVECERIA 244 y SUSHI 18, sale CONFITERIA 379). El **ampliado no cambia**: 10.888
parcelas. Es una propiedad útil de esta decisión — mueve una categoría entre anillos sin alterar
el universo total, así que las dos lecturas siguen siendo comparables.

La razón contra el padrón baja de 1,38 a **1,33**, y el patrón que importa no se mueve: sigue
siendo más alta donde el padrón es más delgado — Villa Soldati 2,91, La Boca 2,13, Villa
Riachuelo 2,04, Nueva Pompeya 2,00, Villa Luro 1,98, Villa Lugano 1,82.

**Pendiente anotado, sin ejecutar:** el mapeo `confiteria → Pastelería` del padrón es discutible
—una confitería porteña es un café con servicio de mesa—, pero corregirlo de un solo lado rompe
la comparación entre bases. Queda registrado en el encabezado de `perfilar_usos_suelo.py` con la
condición de que, si se cambia, se cambia en las dos fuentes en la misma corrida.

### Decisión 2 · El oeste entra en esta tanda

Hechas las veinte fichas documentales: doce del oeste y ocho del sur, con las dos condiciones
implementadas —sin factor de captura, y con la añada del Relevamiento declarada en cada una—.
Están en `generado/FICHAS_DOCUMENTALES_OESTE_SUR.md`.

| grupo | barrios | parcelas núcleo | parcelas ampliado | direcciones núcleo | oferta F01 |
|---|---:|---:|---:|---:|---:|
| Oeste | 12 | 1.340 | 1.708 | 968 | 224 |
| Sur | 8 | 772 | 978 | 456 | 175 |

Anotado para cuando se corra Places: **empezar por el oeste**, que es donde el dato documental
está más viejo. Nueve de los doce barrios se relevaron en 2022.

### Decisión 3 · Habilitaciones como control, Relevamiento como columna

Implementado así. Las 22 zonas ahora tienen las dos columnas y **el rango de control sigue siendo
el de habilitaciones**. Resultado en §2.

---

## 2 · El segundo rango calibrado

| método del Atlas | zonas | captura contra habilitaciones | captura contra Relevamiento |
|---|---:|---|---|
| Directorio comercial en línea | 4 | 92,6 % (80,0 – 116,8) | **114,5 %** (106,9 – 139,5) |
| Mínimo relevado | 7 | 30,4 % (13,9 – 57,3) | 44,9 % (16,7 – 52,5) |
| **Relevamiento propio** | 4 | **18,2 %** (7,6 – 36,1) | **29,0 %** (22,4 – 52,5) |
| Relevamiento anterior | 2 | 9,2 % (4,2 – 14,3) | 19,1 % (una sola zona medible) |

**El rango de control de relevamiento propio queda en 7,6 – 36,1 % contra habilitaciones, y su
equivalente contra el Relevamiento es 22,4 – 52,5 %.** Los dos se informan juntos; el primero es
el que decide si una zona nueva se relevó igual que las anteriores.

Lo que agrega la segunda columna: **las cuatro zonas de directorio comercial superan el 100 %**.
El Relevamiento encuentra en esos perímetros más parcelas gastronómicas que locales publicados.
Devoto llega a 139,5 %. Eso refuerza, desde otra fuente, que esas cuatro cifras son de escala
documental y no de relevamiento.

### La mezcla de añadas, zona por zona

Era el riesgo que había que medir antes de usar la segunda columna, y resultó menor de lo
temido. De las 17 zonas con cifra publicada:

- **8 zonas tienen el 100 % de sus parcelas de un solo año.**
- **13 tienen el 90 % o más de un solo año.**
- **3 mezclan de verdad**, y son las que llevan la declaración obligatoria:

| zona | mezcla |
|---|---|
| R13 · Abasto | 2023: 45,9 % · 2024: 54,1 % |
| R19 · Federico Lacroze por tramos | 2023: 54,2 % · 2024: 45,8 % |
| R21 · La Paternal | 2022: 24,2 % · 2023: 75,8 % |

Las 19 zonas que cruzan más de un barrio no heredan automáticamente una mezcla de añadas: la
superficie se reparte entre barrios, pero las parcelas gastronómicas tienden a concentrarse en el
tramo principal, que casi siempre es de un solo barrio. La mezcla se calcula sobre las parcelas
contadas, no sobre la superficie, y por eso da más limpia de lo que el crosswalk sugiere.

### Dos correcciones que salieron de verificar el crosswalk

**El crosswalk está calculado sobre las envolventes crudas.** Reproduce exacto —22 de 22 zonas
con desvío ≤ 0,1 pp— cuando se usan las envolventes sin descontar el solape. La capa de conteo usa
los perímetros con precedencia, y para dos zonas eso cambia el reparto por barrio:

| zona | crosswalk (envolvente cruda) | perímetro efectivamente contado |
|---|---|---|
| R12 | San Nicolás 54,5 · Retiro 25,4 · Monserrat 20,1 | San Nicolás 48,4 · Retiro 28,8 · Monserrat 22,8 |
| R18 | Retiro 71,7 · San Nicolás 28,3 | Retiro 44,7 · **San Nicolás 55,3** |

En R18 la diferencia es de 27 puntos y da vuelta cuál es el barrio dominante. Para declarar la
añada de esas dos zonas hay que usar la segunda fila, no el crosswalk.

**R07 · Costanera Norte no tiene factor de captura contra el Relevamiento**, y su cero no es un
cero. En ese perímetro de 38,5 hectáreas el Relevamiento tiene **una sola parcela**: es tierra no
parcelada sobre el río. La densidad de parcelas relevadas es de 0,03 por hectárea contra 15,6 en
la Ciudad; la zona más floja de las otras veintiuna tiene 10,8 y no hay ninguna en el medio. Se
informa como «sin cobertura», no como 0 %. Dejarlo en cero habría metido una medición falsa en la
mediana de su método.

---

## 3 · El detector de lotes de permisos

El patrón de R18 no era una excepción: **45 lotes, 137 direcciones, 9.697 habilitaciones — el
22,6 % del padrón georreferenciado.**

Y hay una prueba mejor que las cuatro señales previstas. El crudo de 2025 trae
`nropartidamatriz`, la partida del inmueble, que permite el test decisivo:

- Los 23.694 registros crudos de esas direcciones se reducen a **658 permisos distintos**.
- La proporción de registros que son repetición: **mediana 96,4 %**, mínimo 83,3 %.
- Un mismo permiso —misma razón social, mismo rubro— llega a figurar en **15 puertas distintas**.
- Una sola partida matriz abarca **44 direcciones** del padrón.
- Las 137 direcciones tienen el 100 % de sus registros sin fecha de habilitación.

Los cinco lotes mayores:

| lote | cuadra | barrio | direcciones × hab. | registros |
|---|---|---|---|---:|
| L01 | Viamonte 500-599 | San Nicolás | 10 × 120 | 1.200 |
| L02 | Falcón 7100-7199 | Liniers | 15 × 65 | 975 |
| L03 | Florida 700-799 | San Nicolás | 8 × 120 | 960 |
| L04 | Córdoba Av. 500-599 | Retiro | 4 × 120 | 480 |
| L05 | Suárez, José León 0-99 | Liniers | 7 × 65 | 455 |

Los tres primeros y L04 son el mismo complejo del microcentro visto desde sus cuatro frentes de
manzana. **Los dos de Liniers son un hallazgo nuevo**, y explican por qué Liniers aparece cuarto
en la Ciudad por volumen de trámite con apenas 114 direcciones núcleo: son 26 direcciones y 1.690
habilitaciones de carga replicada. La ficha de Liniers lo advierte.

Una señal prevista **no se pudo medir**: la correlatividad de expedientes. El `id_habilitacion`
del modelo es una clave nuestra, no el número de expediente, y probarlo daba tiradas de largo 1.
El expediente real no está en el modelo. Se reemplazó por la partida matriz, que es más fuerte.

**Ninguna cifra publicada está afectada** —la regla 3 ya excluye estas direcciones del conteo—.
Lo que hay que cambiar es la lectura: la columna `habilitaciones` no sirve como indicador de
volumen y va siempre al lado de `dir_outlier`. El listado nominado sirve como consulta de calidad
de carga para la AGC.

---

## 4 · Los dos controles nuevos en el código

**Doble codificación como control, no como limpieza.** `verificar_codificacion()` corta la corrida
si queda algún valor con marcadores CP437 después de reparar. Y se agregó un segundo control que
no estaba pedido pero cubre el mismo riesgo por el otro lado: `verificar_vocabulario()` falla si
la fuente deja de tener alguno de los valores de `TIPO2` que el mapeo declara. Probados los dos
contra casos negativos: cortan cuando deben y pasan cuando el valor está reparado.

Sin esto, una fuente futura con el mismo defecto borraría 1.803 parcelas de café sin que nada
falle. Con esto, falla.

**Conciliación 6.861 / 7.181.** Documentada y calculada en `build_capa_homogenea.py`, que ahora
imprime `7.181 en CABA = 6.861 sumadas por barrio + 320 anómalas que son núcleo`. De las 324
direcciones anómalas, 320 son del anillo núcleo; el titular las incluye y la suma por barrio las
excluye por la regla 3. El número comparable contra parcelas es el segundo.

---

## 5 · Un hallazgo lateral que conviene registrar

Los crudos de F02 de 2015 a 2024 traen `seccion`, `manzana` y `parcela`: **la misma clave
catastral SMP que usa el Relevamiento de Usos del Suelo.** Es un camino de unión directo entre
padrón y Relevamiento, parcela contra parcela, sin pasar por direcciones normalizadas ni por
geometría. No se usó todavía. Si funciona, resuelve de raíz el problema de emparejar las dos
bases.

Advertencia de manejo: esos crudos también traen `titulares`, `cuits` y `telefono`. El detector
está escrito para no leer esas columnas, y de `razon_social` sólo informa conteos.

---

## 6 · Places · conteo de requests, sin ejecutar

**Ninguna llamada hecha.** `estimar_costo_places.py` no toca la red.

La grilla de 1.190 celdas se reprodujo desde km² y universo esperado: **48 de 48 barrios
coinciden** con el CSV.

| corrida | celdas | requests estimados | cota ×3 |
|---|---:|---:|---:|
| Paso 1 · control de las 17 zonas con cifra publicada | 190 | **301** | 570 |
| Paso 1 reducido · sólo las 4 relevadas a pie (R08-R11) | 51 | **102** | 153 |
| Paso 2 · barrido de los 48 barrios | 1.190 | **2.100** | 3.570 |
| **los dos juntos** | | **2.401** | 4.140 |

Contra la franja gratuita de 5.000 llamadas por mes del SKU Pro, **los dos pasos entran en un
mismo mes con 2.599 de margen**. El estimado de 2.100 cuenta páginas y no consultas: cada celda
cuesta un request y se paga una página más sólo donde el universo esperado supera los 20
resultados. La cota ×3 es el peor caso, y también entra.

Una observación sobre la grilla: **en 27 barrios la manda la superficie y no la densidad**, y ahí
se pagan celdas que van a volver casi vacías — Villa Soldati 35 celdas para 60 locales esperados,
Villa Lugano 38 para 280. Esos 27 barrios cuestan 644 requests de los 2.100; bajarlos a celdas de
1 km ahorraría la mayor parte sin perder cobertura. Como el total entra igual en la franja, es una
optimización, no un bloqueo.

**El precio por encima de la franja sigue sin confirmar.** No hace falta para estas dos corridas,
pero sí antes de cualquier profundización por familias de query.

---

## 7 · Límites

- El Relevamiento **no es «locales abiertos hoy»**: es uso de parcela al momento del censo, con
  año distinto por barrio. Cada ficha lo declara.
- La equivalencia de rubros ahora es simétrica con el padrón, pero **hereda los criterios del
  padrón**, incluido el discutible `confiteria → Pastelería`.
- El factor de captura **no es una propiedad de la zona** sino del par (método, base de
  contraste), y no se reporta sin decir contra qué se calculó.
- Las 24.483 parcelas unicomerciales con `TIPO2` sin identificar siguen fijando el techo de
  precisión de cualquier conteo sobre esta fuente.
- El detector de lotes sólo puede usar la partida matriz en la cohorte 2025, la única que la trae.
  Los lotes de cohortes anteriores, si existen, quedan sin ese respaldo.
- Ninguna cifra publicada del Atlas se modificó. La edición técnica sigue siendo la V2.1 sellada,
  y las fichas del oeste y del sur son un producto separado.

---

## 8 · Estado del orden pedido

| paso | estado |
|---|---|
| 1 · aplicar las tres decisiones y regenerar | **hecho**; las tres tablas siguen reproduciendo la referencia con `--check` |
| 2 · recalcular las 22 contra el Relevamiento con la mezcla de añadas | **hecho** |
| 3 · fichas documentales del oeste y del sur | **hecho**, 20 fichas |
| 4 · Places | **estimado, no ejecutado**: 301 + 2.100 requests |

Lo que queda para tu decisión: autorizar la corrida del Paso 1 de Places con esos 301 requests
—o los 102 de la versión reducida— y si se baja la grilla de los barrios grandes y poco densos
antes del barrido completo.

---

## Anexo · Archivos

| ruta | qué es |
|---|---|
| `scripts/barrido_ciudad/build_capa_homogenea.py` | las tres tablas, con `--check` y la conciliación |
| `scripts/barrido_ciudad/perfilar_usos_suelo.py` | anillos por simetría + los dos controles con corte |
| `scripts/barrido_ciudad/capa_rus_por_zona.py` | las 22 zonas sobre el Relevamiento, añadas y cobertura |
| `scripts/barrido_ciudad/detectar_lotes_permisos.py` | el detector, con la prueba de partida y replicación |
| `scripts/barrido_ciudad/build_fichas_documentales.py` | las 20 fichas del oeste y del sur |
| `scripts/barrido_ciudad/estimar_costo_places.py` | conteo de requests, sin red |
| `generado/factor_captura_22_zonas_dos_bases.csv` | el factor con las dos bases y la añada por zona |
| `generado/capa_rus_22_zonas.csv` | la capa del Relevamiento por zona, con cobertura |
| `generado/lotes_permisos_detectados.csv` | las 137 direcciones agrupadas en 45 lotes |
| `generado/lotes_permisos_replicacion.csv` | la evidencia de replicación por lote |
| `generado/direcciones_anomalas_324.csv` | las 324 anómalas con todas las señales medidas |
| `generado/FICHAS_DOCUMENTALES_OESTE_SUR.md` | las fichas |
| `generado/ESTIMACION_PLACES.txt` | el detalle del conteo de requests |
