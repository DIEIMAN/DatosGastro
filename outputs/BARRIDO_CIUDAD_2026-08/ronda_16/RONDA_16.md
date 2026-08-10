# Ronda 16 · la capa administrativa y los siete que faltan · 2026-08-10

Tres tareas: la contabilidad de erratas, el control de la capa administrativa oficial, y convertir
«a cinco les faltan cuatro palabras» en una lista que alguien pueda ir a buscar.

**Google Places: 0 requests.** No se tocó ninguna capa publicada, ni `zonas_r8.geojson`, ni las
fichas, ni la capa de barrios. **No se corrió `git commit`.**

Salidas: `capa_administrativa.csv` · `que_falta_por_zona.csv` · sus dos scripts.

---

## 1 · La renumeración, que era lo que bloqueaba

Hecha. Las cinco erratas de la ronda 15 pasan de **ERR-17…ERR-21** a **ERR-22…ERR-26**:

```
ERR-22  Necochea: el perímetro de la obra pública no contiene ninguna de sus cinco anclas
ERR-23  Villa Ortúzar: dos tercios del corredor están en Colegiales y Chacarita
ERR-24  Almagro: el corredor de Corrientes está 70 % adentro del Abasto
ERR-25  Villa Luro: la ficha escribe la misma pieza dos veces, y difieren 256 m
ERR-26  la capa de hitos trae ocho filas repetidas
```

Actualizados `RONDA_15.md`, `errata_2026-08-10_ronda_15.csv` y verificado `RONDA_15.txt` —que no
emitía ningún id, así que no requirió cambios—. El mapeo quedó escrito arriba de `RONDA_15.md`
para que nadie lo reconstruya de memoria.

**Confirmado por barrido:** ERR-17, ERR-18 y ERR-19 viven en `CRITERIO_DE_ADMISION_Y_PERMANENCIA.md`,
`TABLERO_ATLAS_V3.md`, `ATLAS_V3_DOCUMENTO.md` y `VERIFICACION_RONDA_15_CODEX.md`, y **no se
tocaron**: ahí son correctos. ERR-22 en adelante estaba libre.

---

## 2 · La capa administrativa: la procedencia verifica, y el diagnóstico de los tres se da vuelta

**Los dos sha256 verifican** contra `PROCEDENCIA_capas_administrativas.json`, 48 barrios y 15
comunas, EPSG:4326.

### Lo que hay que corregir del planteo, y es una sola medición

La tarea decía que Z41 Núñez y Z45 Belgrano *«declaran ser polígono administrativo de X y no lo
son»*. **Medido, sí lo son.** Antes de documentar una suma o revertir un polígono hay que saber
quién puso la diferencia, y eso se decide comparando la zona contra **las dos** capas de barrios:

```
                    zona menos capa VIEJA     zona menos capa OFICIAL    veredicto
Z41 Núñez                    0 m²                   74.837 m²           el atlas no sumó nada
Z45 Belgrano                 0 m²                   65.152 m²           el atlas no sumó nada
Z46 Retiro             149.485 m²                  156.196 m²           el atlas SÍ sumó
```

**Z41 y Z45 son idénticas a `data/raw/geo_barrios.geojson`, la capa que el atlas viene usando:
diferencia simétrica 0 m².** Su campo `detalle_geometria` es exacto. Toda la diferencia contra la
capa oficial es **entre las dos capas de barrios**, no entre el atlas y su barrio.

**Z46 sí sumó, y su campo ya lo declara:** una pieza de 149.485 m² con 117 locales, **100 % en San
Nicolás** — el clúster coreano-asiático. Confirmado, nada que hacer.

### Dónde difieren las dos capas, sobre los 48 barrios

```
la Ciudad entera:   vieja 20.408,31 ha   ·   oficial 20.375,17 ha
  vieja menos oficial:  366.931 m²  con  0 locales
  oficial menos vieja:   35.519 m²  con  1 local
```

**Los cuatro barrios que difieren más del 0,5 % son Recoleta, Palermo, Núñez y Belgrano: los cuatro
del frente costero.** La diferencia es la línea de ribera del Río de la Plata, y **no lleva
locales**. El sobrante de Núñez son 74.837 m² con **0 locales**; el de Belgrano, 65.152 m² con **1**.

**Doce barrios cambian su conteo de locales, todos por 1 o 2, con un neto de +1 en toda la Ciudad.**
Son locales sentados exactamente sobre un límite que se movió unos metros.

### Lo que recomiendo, y lo que no hice

Ninguna de las dos salidas que planteaba la tarea aplica: **no hay nada que documentar** —el atlas
no sumó nada— y **«volver al oficial» no es un parche por zona**: es cambiar la capa de barrios
para los 48, lo que mueve el conteo de doce de ellos.

**Recomiendo adoptar `caba_barrios.geojson` como canónica**, por una razón sola: tiene procedencia,
commit y sha256 verificables, y `data/raw/geo_barrios.geojson` no tiene ninguno. El costo está
medido y es chico: doce barrios ±1 local, y los `ha_del_provisorio` de la ronda 15 se mueven en
Núñez (449,86 → 442,64), Belgrano y Retiro.

**No lo hice**, porque `polos_soporte.barrios()` alimenta mediciones de varias rondas y cambiar la
capa por mi cuenta movería números que ya circularon. **Es una decisión de una línea y es de Diego.**

> **Y una trampa de integración que conviene levantar antes de que muerda:** la capa vieja escribe
> **`La Boca`** y la oficial **`Boca`**. Cualquier cruce por clave normalizada **pierde el barrio
> entero en silencio.** El script lo detecta y lo empareja a mano; quien use la capa oficial en otro
> lado tiene que hacer lo mismo.

---

## 3 · Los siete que faltan: `que_falta_por_zona.csv`

**16 piezas de 11 zonas** — las 10 de los siete sin trazar, más las 6 piezas sin cerrar de las
cuatro «parcial», que son las que impiden que esas fichas publiquen cifra. Cada fila lleva el dato
que falta, **la frase exacta de la ficha donde está el hueco**, dónde vive esa frase, y quién puede
conseguirlo.

**A nueve de las dieciséis les falta sólo un tramo o un rango de alturas.** Ése es el trabajo de
mayor rendimiento que queda, y no lo puede hacer el repositorio.

Donde el atlas ya tenía en disco un número que podría llenar el hueco, se midió qué daría, en la
columna `candidato_medido_NO_adoptado`. **Ninguno se adopta**, y el motivo está en cada fila:
varios vienen del eje del IDECBA o de las direcciones de los referentes, y las dos cosas describen
otro objeto que el perímetro del polo.

### Cuatro hallazgos de esta pasada

**Parque Avellaneda: Av. Olivera no bordea el parque.** La cara del parque mide 44,21 ha con cero
locales y tiene **911 m de frente sobre Av. Lacarra y 614 m sobre Av. Directorio** — que la ficha
no nombra. Sobre Av. Olivera tiene **0 m**: la toca en un punto. Y la fuente que la ficha cita
—Time Out— habla de bodegones **sobre** Olivera y Lacarra, que es un corredor. **«Anillo» es palabra
del atlas, no de la fuente**, y describe una figura que la geometría no sostiene. Hay que elegir:
o es un corredor en L y faltan dos rangos de alturas, o es el anillo y la segunda avenida es
Directorio.

**Barrio Charrúa: los tres bordes no cierran, y por dos motivos.** Las vías del Belgrano Sur no son
una línea del callejero —sólo hay segmentos con marca de cruce—, y **Av. Bonorino y Av. Fernández
de la Cruz se cruzan**, igual que las de Parque Avellaneda. Poniendo el borde del barrio como
tercer lado, la cara que sale es **Nueva Pompeya entera: 493,69 de sus 495,41 ha**.

**Balvanera tiene un perímetro redactable, y está redactado.** Es la única a la que la tarea pedía
escribirle uno. Sale de las puertas que su propia ficha ya lista, todas del padrón oficial de 2015:

> **«Eje Tucumán entre el 2379 y el 2755, ambas aceras, con transversal sobre Paso al 700.»**

Las cinco direcciones resuelven en el callejero y Paso cruza el tramo. Medido daría **19,18 ha y 74
locales**. **No se adopta**: es una propuesta de redacción para quien escribe la ficha, y el padrón
del que sale es de 2015.

**El corredor del viaducto de Núñez ya se dibujó una vez, y por eso no cuenta.**
`seis_vias/nunez_corredor_viaducto.geojson` existe: 48,96 ha, y su propio campo dice *«aprox. recta
entre cabeceras»* con **buffer de 150 m**. Es exactamente el borde que esta ronda no admite —una
propiedad del instrumento— y confirma que la pieza sigue sin perímetro.

---

## 4 · Z40 y la fusión con Z54: la decisión no está esperando a la geometría

Z40 **no cierra**: sus tres piezas necesitan un rango de alturas cada una, y la del Barrio Charrúa
además un cuarto borde que no existe.

**Pero la fusión que está bloqueada no depende de eso.** Puestos los dos perímetros escritos al
lado:

| | perímetro escrito |
|---|---|
| **Z40**, pieza 2 | «**Av. Sáenz y el Mercado de Pompeya**» |
| **Z54** | «Eje **Av. Sáenz**, con núcleo en el **Mercado de Pompeya, Av. Sáenz 790**» |

**Son el mismo eje y el mismo objeto, a la misma dirección.** Z54 no es una zona que se solape con
Z40: es una pieza que **el perímetro de Z40 ya lista**. La medición de Codex —Z54 cae 100 % dentro
de Z40— llega al resultado correcto por el camino equivocado, porque midió contra el polígono del
barrio; el que sostiene la conclusión es el texto, no la geometría.

**Lo que espera al perímetro de Z40 es la cifra, no la decisión.** La fusión se puede firmar hoy;
cuánto mide el objeto fusionado, no.

> Y para cuando se decida el tramo: el candidato en disco para esa pieza es **Av. Sáenz 790-1399**
> —el mercado en el 790 y el eje del IDECBA del 801 al 1399—, que daría **39,39 ha y 52 locales**.
> Adoptarlo sería decidir que el polo coincide con el eje relevado por la Ciudad, que es
> exactamente lo que Mataderos no dejó hacer. Queda medido y sin adoptar.

---

## 5 · Lo que esta ronda NO hizo

- **No cambió la capa de barrios.** La recomendación de §2 es una decisión de Diego y mueve doce
  conteos.
- **No adoptó ningún perímetro nuevo.** Los diez candidatos medidos viajan marcados como no
  adoptados, incluida la redacción propuesta para Balvanera.
- **No tocó las erratas de Cowork** ni los documentos donde ERR-17/18/19 son correctos.
- **No corrió `git commit`**, como estaba pedido.
- **No resolvió los arrastres**: ERR-11, ERR-12, el normalizador de calles, los 584 de Palermo, la
  cuña de Colegiales, los 10 `requiere_cruce` de la vía E, la vía B contra el catálogo cargado y la
  atribución del eje Triunvirato siguen abiertos.
