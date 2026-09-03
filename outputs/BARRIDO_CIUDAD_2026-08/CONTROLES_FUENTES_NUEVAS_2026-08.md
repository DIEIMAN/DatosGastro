# Barrido de la Ciudad: capa homogénea portada al repositorio y controles de las fuentes nuevas

> **Continuado por `APLICACION_DECISIONES_2026-08.md`.** Las tres decisiones que este informe
> dejaba pendientes están resueltas allí. En particular, CONFITERIA pasó al anillo ampliado, así
> que **las cifras del Relevamiento de este documento quedan superadas**: el núcleo de la Ciudad
> es 9.108 parcelas y no 9.440, y la razón contra el padrón es 1,33 y no 1,38. El resto del
> contenido —los dos controles, el veredicto del MOC, el caso R18 y la propuesta del oeste— sigue
> vigente.

**Fecha:** 5 de agosto de 2026
**Alcance:** Paso 1 (portar la capa homogénea) y Paso 2 (evaluar las dos fuentes nuevas).
**No incluye:** Paso 3 (relevamiento de Núñez y La Boca) ni el diseño de Google Places, que
quedan a la espera de la decisión sobre el Relevamiento de Usos del Suelo.

---

## 1 · Resumen

1. **La capa homogénea ya se reproduce desde el código.** El generador vuelve a dar las tres
   tablas de agosto celda por celda, incluido el orden de las filas: 48 barrios, 22 zonas y el
   factor de captura. El control de aceptación está automatizado.
2. **El Relevamiento de Usos del Suelo separa gastronomía, y la separa bien.** No hay que
   inferirla: `TIPO2` trae un vocabulario propio con RESTAURANTE, CAFÉ, BAR, PIZZERIA, PARRILLA,
   HELADERIA y cinco categorías de comida al paso, todas bajo `TIPO1 = UNICOMERCIAL`. La
   correspondencia con nuestros dos anillos es casi uno a uno. **Sirve como fuente primaria del
   barrido.**
3. **Cubre los 48 barrios y ningún barrio queda vacío**, pero **no es una foto simultánea**: el
   relevamiento es rotativo y cada barrio tiene un solo año —11 barrios en 2022, 19 en 2023 y 18
   en 2024—. Eso condiciona qué comparaciones son legítimas.
4. **El MOC sí exporta datos crudos, y con una tabla de cierres**, pero no resuelve el problema
   de vigencia: la serie termina en 2017 y la unidad no es un conteo de bajas sino un nivel
   ordinal de 1 a 5.
5. **R18 · Esmeralda–Paraguay queda explicada:** 12 direcciones concentran el 92,7 % de las
   habilitaciones de la zona y once de ellas son **el mismo lote de 120 permisos replicado
   puerta por puerta** sobre la cuadra de Florida y Av. Córdoba. No son locales.
6. **El oeste conviene incorporarlo en esta tanda**, con el Relevamiento como base y sin salir a
   la calle. El argumento está en la sección 7.

---

## 2 · Paso 1 · La capa homogénea, ahora en el código

Generador: `scripts/barrido_ciudad/build_capa_homogenea.py`. Solo lectura sobre
`data/processed/`, `data/raw/` y `outputs/polos_gastro/ATLAS_V2/capas/`; escribe únicamente en
`outputs/BARRIDO_CIUDAD_2026-08/generado/`. No toca el pipeline público F01–F05 ni los CSV de
referencia.

Con `--check` compara contra las tablas de agosto:

```text
habilitaciones gastronómicas georreferenciadas: 42.836
direcciones distintas: 7.829
habilitaciones por dirección: 5.5
direcciones anómalas (>20 habilitaciones): 324 = 46.9 % de los registros
direcciones núcleo en CABA: 7.181
direcciones ampliado en CABA: 7.826

  [OK] capa_homogenea_48_barrios.csv: 48 filas x 5 columnas idénticas, orden de filas igual
  [OK] capa_homogenea_22_zonas.csv: 22 filas x 5 columnas idénticas, orden de filas igual
  [OK] factor_captura_22_zonas.csv: 22 filas x 6 columnas idénticas

RESULTADO: reproduce la capa exacta
```

Las cinco reglas de conteo quedaron escritas como código y no como criterio: la unidad es
`id_ubicacion`; los dos anillos son constantes declaradas al inicio del archivo; el umbral de
dirección anómala es una constante; la asignación es `sjoin` punto en polígono; y la ventana no
se filtra, con la advertencia sobre bajas en el encabezado.

### 2.1 · Tres reglas que estaban implícitas y ahora están explícitas

Reproducir las tablas exigió reconstruir tres decisiones que el documento de método no
mencionaba. Vale registrarlas porque de otro modo la próxima corrida las volvería a perder.

| decisión | cómo quedó resuelta |
|---|---|
| **Superposición de envolventes** | Dos pares se solapan: el eje Corrientes (R02) atraviesa el microcentro segmentado (R12), y R18 está contenido en R12 en un 64 % de su superficie. El perímetro de menor `referencia_id` retiene la superficie compartida, de modo que ninguna dirección se cuenta dos veces en el mismo cuadro. Sin esta regla, R12 daría 370 en lugar de 327 y R18 daría 104 en lugar de 30. |
| **Barrio de la oferta F01** | F01 trae su propio campo `barrio`; se conserva cuando el punto cae dentro de ese polígono y se reemplaza por el barrio geométrico cuando no. Un punto sobre los diques no cae en ningún barrio y queda sin asignar. |
| **Orden de presentación** | Los 48 barrios se ordenan por base núcleo y, a igualdad, por oferta F01. |

Las cifras publicadas del Atlas y el método de cada zona **no se recalculan**: se declaran en
`insumos/cifras_publicadas_atlas_22.csv` y el generador solo divide para obtener la captura.

---

## 3 · Paso 2 · Relevamiento de Usos del Suelo · Control 1: el vocabulario

Archivo bajado: 39,5 MB, 417.764 registros sobre **318.607 parcelas** distintas. `TIPO2` tiene
**471 valores distintos** y 15.637 registros sin valor. Script: `scripts/barrido_ciudad/perfilar_usos_suelo.py`.

La respuesta al control es que **sí separa gastronomía**, y con más detalle que nuestro propio
padrón. Correspondencia con el anillo núcleo, en parcelas activas:

| nuestro anillo | valores de `TIPO2` | parcelas activas |
|---|---|---:|
| Restaurante | RESTAURANTE | 2.666 |
| Comida al paso | COMIDAS PARA LLEVAR 1.142, COMIDA RAPIDA 462, EMPANADAS 388, ROTISERIA 304, SANDWICHERIA 88 | 2.384 |
| Café | CAFÉ 1.715, CAFÉ (VTA AL PASO) 88 | 1.803 |
| Pizzería | PIZZERIA | 988 |
| Bar | BAR | 883 |
| Heladería | HELADERIA | 779 |
| Parrilla | PARRILLA | 333 |
| | suma de las categorías | 9.836 |
| | **parcelas distintas** | **8.877** |

Las dos últimas filas no coinciden y la diferencia importa: **764 parcelas tienen más de un uso
gastronómico relevado**, así que sumar categorías sobrestima en un 11 %. Es la regla 1 otra vez,
en versión suave: la unidad es la parcela, no el registro de uso. El script cuenta `SMP`
distintos.

Tres valores más requieren tu decisión, y por eso se informan aparte: **CONFITERIA 379,
CERVECERIA 244 y SUSHI 18**. En esta corrida se cuentan dentro del núcleo, y suman 563 parcelas:
el núcleo pasa de 8.877 a 9.440. No cambia ninguna conclusión, pero conviene fijarlo antes de
publicar.

El anillo ampliado suma **PANADERIA 1.691**. Dos categorías nuestras **no tienen equivalente**:
Pastelería, cuyo pariente más cercano es CONFITERIA, y Catering, que el Relevamiento no registra
porque no ocupa local a la calle.

Y hay trece valores que la búsqueda por palabra clave trae y **no** son gastronomía de atención
al público: BARBERIA 661, ALIMENTOS PARA MASCOTAS 505, FABRICA DE PASTAS 372, VINOS (VENTA) 328,
BEBIDAS ALCOHOLICAS 287, GALERÍA BARRIAL 202, VENTA POR MAYOR DE ALIMENTOS Y BEBIDAS 81,
EQUIP. GASTRONOMICO 26, VENTA DE CAFÉ (PRODUCTOS) 25, REPARACION DE HELADERAS 20,
HELADERAS Y BALANZAS COMERCIALES 10, RESTAURACIONES 12 e INSTITUTO DE GASTRONOMIA 2. Están
excluidas por lista explícita en el script, no por criterio de corrida.

**Dato lateral con valor propio:** el Relevamiento trae `ESTADO` activo/inactivo por parcela.
Hay **200 parcelas gastronómicas inactivas** al momento de relevarlas. Es un indicador de local
vacante en el momento del censo —no una baja registrada—, pero es lo más cercano a vacancia que
tenemos en una fuente oficial.

---

## 4 · Control 2: cobertura y completitud

| año del relevamiento | barrios | parcelas |
|---|---:|---:|
| 2022 | 11 | 65.696 |
| 2023 | 19 | 143.086 |
| 2024 | 18 | 109.825 |
| **total** | **48** | **318.607** |

**Los 48 barrios están presentes y ninguno queda vacío.** Ningún barrio tiene más de un año, lo
que confirma que el operativo es rotativo: se releva por barrio y se publica con el año en que
se hizo.

Barrios de 2022 (los más desactualizados, con tres años de antigüedad): Agronomía, Monte Castro,
Parque Chas, Vélez Sarsfield, Versalles, Villa del Parque, Villa Devoto, Villa Gral. Mitre,
Villa Luro, Villa Real y Villa Santa Rita. **Nueve de los once son del oeste**, que es
justamente la zona que se propone incorporar; hay que decirlo al publicar.

### 4.1 · Qué encuentra, comparado con las habilitaciones

Sobre los 48 barrios: **9.440 parcelas gastronómicas activas** contra **6.861 direcciones
núcleo** del padrón de habilitaciones. Razón 1,38.

Lo relevante no es el total sino **dónde** aparece la diferencia:

| barrio | direcciones núcleo (habilitaciones) | parcelas núcleo (Relevamiento) | razón |
|---|---:|---:|---:|
| Villa Soldati | 11 | 32 | 2,91 |
| La Boca | 55 | 118 | 2,15 |
| Villa Luro | 42 | 88 | 2,10 |
| Villa Riachuelo | 25 | 52 | 2,08 |
| Nueva Pompeya | 52 | 105 | 2,02 |
| Villa Lugano | 51 | 96 | 1,88 |
| … | | | |
| San Nicolás | 433 | 490 | 1,13 |
| Vélez Sarsfield | 60 | 68 | 1,13 |
| Puerto Madero | 39 | 38 | 0,97 |

**La razón es más alta exactamente donde el padrón es más delgado.** En el centro y en el norte
las dos fuentes casi coinciden; en el sur el Relevamiento encuentra el doble o el triple. Eso
confirma con números lo que la ficha de la fuente afirmaba: tiene la misma densidad en el sur
que en el norte, y el padrón no.

### 4.2 · Veredicto sobre la fuente

**Entra como fuente primaria del barrido**, con las habilitaciones pasando a rol de respaldo
oficial y trazabilidad. Los motivos son tres: mide uso efectivo y no trámite, no arrastra el
problema de las bajas de la misma manera, y su cobertura no se degrada en el sur ni en el oeste.

Esto **cambia el orden previsto**: el piso documental de una zona nueva ya no es «las
direcciones con habilitación» sino «las parcelas relevadas con uso gastronómico», y el número
del padrón queda como segunda columna.

---

## 5 · Control del MOC · Mapa de Oportunidades Comerciales

La plataforma `moc.buenosaires.gob.ar` no responde desde esta máquina —la conexión se corta—,
pero **el dataset está publicado en el portal de datos abiertos** y se bajó completo:
`mapa-oportunidades-comerciales-moc`, actualizado el 24 de junio de 2026.

Trae cinco tablas, y entre ellas **una de cierres**: `apertura.csv` (5.210 filas),
`cierre.csv` (3.114), `rubros.csv` (2.898), `zonas.csv` (161) y las 161 zonas en GeoJSON, que
cubren el **99,6 % de la superficie de la Ciudad**.

Cinco de sus 18 rubros son gastronómicos: RESTAURANTES, BARES Y CAFES, COMIDA AL PASO,
HELADERIAS y PANADERIAS.

**Pero no resuelve el problema de vigencia**, por dos razones que hay que decir juntas:

- **La serie termina en 2017.** Apertura y cierre cubren 2016 y 2017, tres cuatrimestres por
  año. La tabla de zonas está fechada al 1 de julio de 2017. La descripción oficial la define
  como «información histórica».
- **La unidad no es un conteo de bajas.** `NIVEL` es un índice ordinal de 1 a 5: el 95 % de las
  filas de cierre está en nivel 1. No dice cuántos comercios cerraron, dice en qué franja de
  cierres cayó ese rubro en esa zona.

Sumado a que la geografía son 161 zonas de unos 1,9 km² —más gruesas que el barrio—, el MOC
queda como **contraste histórico de dinámica relativa, no como fuente de bajas**. Conviene
bajar la expectativa que tenía en el documento de fuentes: el problema de vigencia sigue abierto
y hoy solo lo cubren el `ESTADO` del Relevamiento y, cuando se ejecute, Google Places.

Nota de tratamiento: `rubros.csv` incluye facturación promedio por zona y rubro. Son agregados
publicados por el GCBA; si se usan, se citan como dato de terceros y no como medición propia.

---

## 6 · El caso R18 · Esmeralda–Paraguay

En el perímetro de R18, descontado el solape con el microcentro, hay **43 direcciones y 1.464
habilitaciones**. **Doce direcciones anómalas concentran 1.357, el 92,7 %.**

Once de esas doce tienen **exactamente 120 habilitaciones cada una y la misma mezcla de rubros**
—Catering 22, Café 22, Bar 22, Comida al paso 16, Heladería 16, Pastelería 16, Restaurante 6—,
todas del año de fuente 2025 y **120 de 120 sin fecha de habilitación**. Las direcciones son
números consecutivos de la misma cuadra: Florida 753, 755, 765, 771, 777, 783 y 785, y
Av. Córdoba 532, 550, 552 y 570. La duodécima, Suipacha 637, repite el patrón con 36.

Eso no es oferta gastronómica: es **un mismo lote de permisos de un complejo cargado contra cada
puerta del frente de manzana**. El perímetro corresponde a la zona de Galerías Pacífico.

Consecuencias prácticas:

- **La cifra de 1.464 habilitaciones de R18 no se publica**, ni como volumen ni como contexto.
- La base defendible de la zona son las **30 direcciones núcleo**, que ya excluyen las anómalas.
- El patrón es detectable y no es exclusivo de R18: el archivo
  `generado/_firmas_repetidas.txt` lista los grupos de direcciones que comparten firma idéntica
  de tamaño y mezcla de rubros. Las dos mayores del padrón —Cabildo 1690 y José Hernández 2412,
  con 360 habilitaciones cada una, dos rubros y 360 expedientes distintos— son del mismo tipo.

La regla 3 del método ya neutraliza esto en el conteo de direcciones. Lo que este caso agrega es
que **la columna `habilitaciones` no es un indicador de volumen** en zonas con muchas anómalas,
y conviene que el tablero la muestre siempre al lado de `dir_outlier`.

---

## 7 · Paso 4 · El oeste, con recomendación

**Recomendación: entra en esta tanda**, por base documental, sin relevamiento de calle.

El argumento cambió con el Relevamiento de Usos del Suelo. Antes incorporar el oeste significaba
mandar gente a doce barrios; ahora significa correr una capa que ya existe y que en el oeste es
tan densa como en Palermo.

| barrio | direcciones núcleo (habilitaciones) | parcelas núcleo (Relevamiento) | año | F01 |
|---|---:|---:|---:|---:|
| Flores | 248 | 343 | 2024 | 85 |
| Liniers | 114 | 173 | 2023 | 20 |
| Villa del Parque | 107 | 155 | 2022 | 9 |
| Mataderos | 92 | 154 | 2023 | 34 |
| Floresta | 81 | 123 | 2023 | 13 |
| Monte Castro | 65 | 92 | 2022 | 15 |
| Villa Luro | 42 | 88 | 2022 | 3 |
| Villa Santa Rita | 52 | 81 | 2022 | 4 |
| Parque Avellaneda | 50 | 69 | 2023 | 14 |
| Vélez Sarsfield | 60 | 68 | 2022 | 13 |
| Villa Real | 38 | 47 | 2022 | 4 |
| Versalles | 19 | 21 | 2022 | 10 |
| **subtotal oeste** | **968** | **1.414** | | **224** |

Para comparar, los ocho barrios del sur suman 456 direcciones núcleo y 793 parcelas. **El oeste
es casi el doble del sur** en base gastronómica y hoy está igual de descubierto.

Flores con 343 parcelas tiene más base que Villa Urquiza, que sí tiene ficha propia en el Atlas.
Liniers es el cuarto barrio de la Ciudad por volumen de trámite.

Dos condiciones para que entre:

1. **Ficha documental, no ficha de zona.** El oeste entraría con el mismo tipo de página que se
   armó para los barrios sin relevamiento: base documental, sin cifra de relevamiento propio y
   sin factor de captura, porque no hay contra qué calcularlo. El factor de captura solo existe
   donde hubo relevamiento.
2. **Declarar la antigüedad.** Nueve de los doce barrios del oeste se relevaron en 2022. Es
   dato de hace tres años y así hay que informarlo.

Si el criterio es priorizar, el orden por base es Flores, Liniers, Villa del Parque, Mataderos y
Floresta; esos cinco concentran el 66 % de la base del oeste.

---

## 8 · Límites

- **La ventana del padrón sigue sin registrar bajas.** Nada de lo hecho acá lo corrige. El
  número documental sigue siendo «direcciones que alguna vez tuvieron habilitación gastronómica
  en la década».
- **El Relevamiento tampoco es «locales abiertos hoy».** Es uso de parcela al momento del
  censo, con año distinto según el barrio. El sustantivo correcto es «parcelas con uso
  gastronómico relevado», con el año al lado.
- **No hay foto simultánea de la Ciudad.** Cualquier comparación entre un barrio de 2022 y uno
  de 2024 mezcla dos momentos. Para rankings entre barrios conviene informar el año de cada uno
  en la misma tabla.
- **24.483 parcelas unicomerciales tienen `TIPO2` = SIN IDENTIFICAR.** Es un 23 % del comercio
  relevado cuyo rubro no se determinó, y fija un techo a la precisión de cualquier conteo
  basado en esta fuente. Puede haber gastronomía ahí.
- **La gastronomía del Relevamiento aparece solo bajo `TIPO1 = UNICOMERCIAL`.** Lo que esté
  dentro de galerías —hay 202 parcelas rotuladas GALERÍA BARRIAL— o en parcelas
  multicomerciales no se enumera por rubro. Es el mismo punto ciego que el caso R18 muestra del
  otro lado.
- **La equivalencia de rubros entre fuentes es una decisión, no un hecho.** CONFITERIA,
  CERVECERIA y SUSHI están hoy en el núcleo por criterio nuestro; Pastelería y Catering no
  tienen equivalente. Sin fijar esto por escrito, dos corridas pueden dar números distintos.
- **Ninguna cifra publicada del Atlas se modificó.** La edición técnica sigue siendo la V2.1
  sellada.

---

## 9 · Próximos pasos

1. **Tu decisión sobre CONFITERIA, CERVECERIA y SUSHI** en el anillo núcleo (563 parcelas en
   juego). Con eso se cierra la equivalencia de rubros.
2. **Tu decisión sobre el oeste**: si entra en esta tanda, se genera la capa de los doce barrios
   sin costo de campo.
3. **Bajar el corte 2017 del Relevamiento** y comparar contra 2022-24. Es la única medición de
   variación real que vamos a tener, y no cuesta nada.
4. **Paso 3 · Núñez y La Boca**, ahora con dos pisos documentales en vez de uno: Núñez 121
   direcciones y 181 parcelas; La Boca 55 y 118. Conviene fijar antes contra cuál se calcula el
   factor de captura, porque el rango de control 8–36 % se estimó contra habilitaciones.
5. **Google Places.** No se avanzó, según lo indicado. Cuando se retome, el conteo de requests
   de la grilla se estima y se informa antes de cualquier corrida con `--run`.

---

## Anexo · Archivos

| ruta | qué es |
|---|---|
| `scripts/barrido_ciudad/build_capa_homogenea.py` | generador de las tres tablas, con `--check` |
| `scripts/barrido_ciudad/perfilar_usos_suelo.py` | los dos controles del Relevamiento y la capa por barrio |
| `outputs/BARRIDO_CIUDAD_2026-08/insumos/cifras_publicadas_atlas_22.csv` | cifras publicadas del Atlas, declaradas |
| `outputs/BARRIDO_CIUDAD_2026-08/generado/` | las tres tablas regeneradas |
| `outputs/BARRIDO_CIUDAD_2026-08/generado/_r18_anomalas.txt` | las 12 direcciones de R18 y las 10 mayores de la Ciudad |
| `outputs/BARRIDO_CIUDAD_2026-08/generado/_firmas_repetidas.txt` | grupos de direcciones con firma de permisos idéntica |
| `data/fuentes_externas/usos_suelo/CONTROLES_RUS_2022_2024.txt` | salida completa de los dos controles |
| `data/fuentes_externas/usos_suelo/rus_gastro_48_barrios.csv` | parcelas gastronómicas por barrio contra habilitaciones |
| `data/fuentes_externas/usos_suelo/rus_vocabulario_tipo2.csv` | los 471 valores de `TIPO2` con frecuencia |
| `data/fuentes_externas/moc/` | las cinco tablas del MOC y el perfil |

Las descargas crudas —el CSV de 39,5 MB del Relevamiento y las tablas del MOC— quedaron
excluidas de Git; las URL de rebaja están en el encabezado de `perfilar_usos_suelo.py` y en
`FUENTES_NUEVAS_2026-08.md`.
