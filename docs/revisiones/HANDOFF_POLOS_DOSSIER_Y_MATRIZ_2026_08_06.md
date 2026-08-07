# HANDOFF · El dossier de medición, la matriz extendida y el corte de la serie R8 · 2026-08-06

Continúa `HANDOFF_POLOS_TANDA_PARALELA_2026_08_06.md`. Rama `mercados-gastronomicos-v2`.
**Google Places: 0 requests.** Ninguna cifra publicada tocada. **Ninguna geometría tocada:**
`polos_publicables.geojson` queda como estaba, marcado como INSUMO. Las 124 fichas no se generaron.

Scripts nuevos: `normalizar_calles.py`, `hitos_unir_capa.py`, `hitos_cruzar_bares_notables.py`,
`polos_control_matriz_v2.py`, `polos_dossier_medicion.py`, `polos_extender_matriz.py`.

---

## 1 · TAREA 4 · El control, primero, porque decide cómo se lee todo lo demás

**La rama que se cumple es la segunda: sirve para CONFIRMAR, no para DESCUBRIR.**

| grupo de la matriz | candidatos | aparecen | no | sin resolución |
|---|---:|---:|---:|---:|
| `incluir_*` | 20 | 13 | 3 | 4 |
| `mencionar_en_anexo` | 7 | 5 | 1 | 1 |
| **`no_incluir_aun`** | **5** | **0** | 4 | 1 |

Tres de los cuatro «sin resolución» de arriba —Soho, Hollywood, Cañitas— ya los había medido
`DONDE_ESTA_SOHO.txt`: contándolos, **16 de 20 aparecen**. Y las **22 envolventes publicadas
tienen las 22 al menos un polo encima**, así que por la otra lectura de «los 22» la respuesta es
completa.

**Ningún candidato descartado a propósito tiene evidencia medida que lo rescate.** Ése era el
hallazgo más valioso posible y no está: los cinco de `no_incluir_aun` siguen sin concentración
propia.

**La salvedad es el anexo**, y no es menor: 5 de 7 aparecen, dos con volumen grande —Abasto con
169 locales en un polo, Parque Patricios con 130—. Si «descartado» incluyera al anexo, la lectura
sería la primera. No se decidió acá: la diferencia entre los dos grupos es de la curaduría.

**Lo que ningún «NO» significa.** Los 8 que no aparecen **tienen polos sobre su envolvente
publicada**. El instrumento no está ciego ahí: encuentra concentración, pero no recortada como el
candidato. Un corredor de avenida con 17 locales con dirección no puede formar un polo cuyo
mínimo es 40.

### Dos sondas, dos umbrales, y por qué no podía ser uno solo

La sonda de **barrio** ve todos los locales; la de **calle** sólo los que tienen dirección, que
son el **50,0 %**. Pedirle 40 a una avenida es pedirle el doble que a un barrio, y ese sesgo
habría caído justo sobre los candidatos descartados, que son casi todos avenidas. La sonda de
calle usa **20**. Sensibilidad sobre los 17 de sonda de barrio: 17/17 a umbral 20, **16/17 a 40**,
13/17 a 80 — el único que se da vuelta es Paternal, con 37 locales contra un mínimo de 40.

### Lo que se decidió NO usar como sonda

La delimitación de Palermo Soho es «Scalabrini Ortiz, Córdoba, Juan B. Justo y Santa Fe»: son sus
**bordes**. Contar los locales sobre esas avenidas mediría el perímetro y no la zona — el mismo
error que tumbó a R18, R19 y R21 como candidatas de Places. Seis candidatos quedan declarados sin
resolución en vez de contestados mal.

## 2 · TAREA 1 · El dossier · `DOSSIER_MEDICION_CANDIDATOS.csv`

**62 candidatos · 4.678 locales · 14 columnas.** Una fila por polo sin ninguna zona publicada
encima, con `polo_id` como identificador de cruce y `barrio_principal` + `calles_dominantes` como
localizador. **No se agrupó, no se redibujó, no se movió ningún umbral.**

Los más grandes: P021 Liniers (262), P073 Palermo (207), P048 Colegiales (171), P076 Recoleta
(156), P037 Villa del Parque (142), P004 Villa Lugano (141).

Distancia a lo publicado, entre puntos: de **74,7 m** a **6.264,9 m**. Los más lejos son del sur y
el oeste —Villa Riachuelo, Villa Lugano, Mataderos, Liniers—, que es exactamente donde ninguna
fuente nombra nada.

**Sólo 20 hitos caen dentro de los 62**, y eso no es un veredicto sobre ellos: es que los
catálogos de distinciones no relevaron esas zonas. Es el encuadre de REFERENTES_2026 —dos
geografías distintas— y viaja en la tabla, no al pie.

## 3 · TAREA 2 · La matriz extendida, con la verificación adentro del script

`matriz_validacion_polos_gastro.csv`: **32 filas × 22 columnas → 94 × 23.**

- Las 22 columnas quedan **en el mismo orden**; `evidencia_relevamiento_propio` va **al final**.
- Las 32 filas viejas están **intactas**: el script las compara celda por celda antes de escribir
  y **aborta si alguna cambió**. Verificado también contra el archivo en disco.
- Las 62 filas nuevas llegan **sin ninguna columna documental** —las llena Diego— y **sin
  `tipo_area`, `nivel_consolidacion`, `estado_validacion` ni `decision_para_informe`**, porque son
  curaduría. `nombre_polo` lleva un localizador (`P021 · Liniers`), no un nombre.
- **39 de 62 caen en el territorio declarado de una fila que ya estaba.** Quedan anotadas en
  `observaciones`, no fusionadas.

**Donde me aparté del pedido, y por qué.** Pediste `si`/`no`. Tres filas llevan
**`sin_resolucion`**: Barrio Chino, Bajo Belgrano y Belgrano R son subzonas de Belgrano y la sonda
trabaja a resolución de barrio. Ahí `no` habría afirmado que no hay concentración y `si` le habría
atribuido a la subzona la del barrio entero. `no` era el valor cómodo y el equivocado.

## 4 · TAREA 3a · El cuarto bicho de la serie R8: **el orden de los tokens**

Salido del inventario, no de casos. Sacando el residuo declarado de las iniciales, lo que quedaba
grande en el bloque (B) era siempre la misma calle escrita en otro orden:

| | |
|---|---:|
| `ROOSEVELT FRANKLIN D` vs `FRANKLIN D ROOSEVELT` | 26 |
| `URIBURU JOSE E` vs `JOSE E URIBURU` | 26 |
| `JUANA MANSO` vs `MANSO JUANA` | 21 |
| `DEL BARCO CENTENERA` en tres formas | 36 |
| `COSTANERA RAFAEL OBLIGADO` en tres formas | 29 |

**Y la causa es la de Niceto Vega con otra ropa: una regla apoyada en una marca que no siempre
está.** La desinversión se dispara con la coma, y la coma falta (`ROOSEVELT FRANKLIN D.`,
`MANSO JUANA`) o separa el tratamiento en vez del apellido (`URIBURU JOSE E., Pres.`,
`OBLIGADO RAFAEL, Av.Costanera`).

**El arreglo es dejar de adivinar el orden, no adivinarlo mejor.** Para agrupar, `clave_calle()`
es el **conjunto** de tokens. Para publicar, `ResolutorDeCalles` elige la etiqueta **con evidencia
y no con una regla de estilo**: el padrón (F01/F02/RUS/PERMISOS) escribe invertido, OSM/Overture/ATP
escriben en orden natural, y gana la forma de las que no invierten. **Acierta 12 de 12, y en 5
corrige a la mayoría simple** —`ROOSEVELT FRANKLIN D` gana 19 a 7 y está al revés—.

El conjunto y no el multiconjunto, porque **absorbe la regla del conector colgando**: una regla se
va en vez de sumarse, y pliega 3 grupos más sin plegar ninguno de más.

Dos bichos que aparecieron en el camino y son del mismo árbol: **la tabla de marcadores tenía `DR`
y no `DOCTOR`**, así que partía Del Valle Iberlucea en dos —ahora es un dict de pares y falta un
lado se ve—; y **`STA FE` no se plegaba con `Santa Fe`**, que se estira porque ahí la palabra es
parte del nombre.

| | antes | después |
|---|---:|---:|
| grupos de sub-plegado | 46 | **31** |
| direcciones afectadas | 1.025 | **824** |
| tests | 23 | **42** |

**16 de 124 polos cambiaron `calles_dominantes`, y ninguna otra columna se movió.** Los que más:
P022 `Ricardo Balbin (8)` + `Doctor Ricardo Balbin (6)` → **`Ricardo Balbin (14)`**; P032
`Valle Iberlucea (5)` → **`Del Valle Iberlucea (10)`, que pasa a ser la calle N.º 1**; P015 tres
formas de Barco Centenera → una de 7.

**El residuo sigue declarado y sin adivinar:** iniciales (`S MARTIN` / `SAN MARTIN`) y artículos de
cabeza (`LA PAMPA` / `PAMPA`). Los dos esperan callejero. Hay **casos negativos en el test** para
cada uno, más `3 DE FEBRERO` ≠ `4 DE FEBRERO` y `TRAFUL N` ≠ `TRAFUL S`.

El normalizador **salió de `polos_foco_menor.py`** —vivía ahí por accidente histórico, y ese
domicilio es parte de por qué se parchó cuatro veces— y vive en `normalizar_calles.py`. Se
reexporta para no romper a quien lo importaba.

## 5 · TAREA 3b · La capa de hitos y los tres conteos de bares

**`hitos_capa_unificada.csv/geojson`: 211 hitos, 181 con punto.** REFERENTES_2026 manda; se
descartan las 148 filas duplicadas **con el descarte anotado por tipo**, no como total. 22 de 23
direcciones nuevas geocodificadas con USIG (no resolvió *Ultramarinos*).

**El número que no da, y lo digo:** la reconciliación estimaba que los mercados pasaban de 2/11 a
**~9/11**. Medido son **8 de 12**. Dos de las ocho direcciones —San Telmo y Costanera Norte— son de
mercados que **ya tenían coordenadas** y no suman cobertura, y Yiyo el Zeneize **no está entre los
11**: entra como fila nueva.

**30 hitos quedan sin coordenadas y no se inventan** — 20 pizzerías y 5 heladerías vienen con
nombre y barrio, sin altura. Ponerlas en el centroide del barrio sería colocar un hito donde no
está.

### Los tres conteos: 84, 95 y 90 → **114 bares distintos, 70 en las tres**

| sólo en | bares |
|---|---:|
| GCBA (84) | 6 |
| Wikidata (95) | 11 |
| Boletín Oficial (90) | 13 |

**Ninguna contiene a las otras.** No se decide cuál manda: eso necesita la fecha de corte y el
acto administrativo de cada lista, y no están en los archivos.

El cruce es por `(calle, altura)` con la clave del normalizador, **comparando la calle por
contención** —`MONTES DE OCA` contra `MANUEL MONTES DE OCA`—, y después por nombre con misma calle
y ±50 de altura. Las 8 fusiones débiles y los 19 pares de homónimos quedan impresos para revisar:
**4 tienen la misma altura** y casi seguro son el mismo bar bloqueado por el residuo de las
iniciales (`Jorge Luis Borges` vs `Jorge L. Borges`); los otros 15 son más probablemente dos bares.

---

## Trampas encontradas hoy

- **Un control puede dar un falso negativo por una diferencia de artículo.** La delimitación dice
  «La Paternal» y la base dice «Paternal»: la comparación literal devolvía **0 locales** y el
  candidato figuraba como «no aparece». Un falso negativo silencioso es lo peor que puede dar un
  control, porque se lee como hallazgo.
- **El mismo umbral sobre dos sondas distintas no es la misma vara.** La sonda de calle ve la
  mitad de los locales; usar 40 en las dos habría castigado justo a los candidatos descartados.
- **La primera versión del cruce fusionó «Café Roma» (Olavarría 409) con «Roma del Abasto» (San
  Luis 3101).** Nombre plegado a secas no alcanza: infla «está en las tres listas», que es
  precisamente lo que el cruce vino a medir.
- **La moda no es la respuesta correcta cuando la mayoría viene de la fuente que escribe mal.**
  `ROOSEVELT FRANKLIN D` gana 19 a 7. Elegir por frecuencia habría publicado la forma invertida.
- **Una condición declarada conviene probarla contra los datos antes de escribirla.** La regla de
  la caja mixta parecía identificar el orden natural y falla: `URIBURU JOSE E., Pres.` tiene un
  token en caja mixta y contamina la señal. La fuente sí funciona, y es dato, no estilo.

## Lo que espera decisión

1. **La matriz quedó bajo control de versiones.** Estaba sin rastrear; como la modifiqué, la
   commiteé para que el cambio no quede desprotegido. Si no querés versionarla, se saca con un
   `git rm --cached` y queda como estaba.
2. **Las 39 filas nuevas que superponen territorio de una fila vieja**: fusionarlas o dejarlas
   como dos miradas del mismo lugar es decisión de curaduría, no de medición.
3. **Los 4 pares de bares con la misma altura y la calle escrita distinto**: si son el mismo bar,
   el conteo «en las tres listas» sube de 70 a 74.
4. **`Ultramarinos`** sigue sin geocodificar y **`Mercado San Nicolás`** y **`Smart Plaza Parque
   Patricios`** sin dirección en ninguna de las dos fuentes.
5. Sigue de antes: los ~7.000 archivos sin rastrear, el saliente N–NE, R01 en la V3 con el 47,7 %,
   el borrado de `places_resumen_por_barrio.csv`, R15 Devoto, R04 Puerto Madero, la cláusula ODbL,
   el visto de Patricia, Bares Notables contra la normativa, Foursquare y el documento extenso del
   método.
