# Panaderías — plan de trabajo

Estado al 2026-08-28. Este archivo es el que se actualiza cuando algo avanza; el
`README_PANADERIAS.md` describe qué es el subproyecto y las `NOTAS_METODOLOGICAS.md`
cómo se construyó el padrón.

## Dónde estamos

| | |
|---|---|
| Universo A (núcleo) | 1.219 |
| Universo B (punto de cocción) | 513 |
| A + B | 1.732 |
| Geolocalizados (A) | 1.203 de 1.219 — **98,7 %** |
| Marcados para revisión manual | 559 |

Cerrado: el lector de F02, el alcance, el clasificador con banco de pruebas, la
geocodificación (control en `outputs/panaderias/analisis/d8_qa_geocodificacion.csv`: 0
puntos fuera de CABA, 2 discrepancias de comuna sobre 116 comparables) y **F1, la unidad
de conteo**.

Abierto y medido: la contaminación por multi-rubro. Ver
`outputs/panaderias/analisis/HALLAZGOS_DIAGNOSTICO.md`.

## El orden en que conviene hacer las cosas

Está ordenado por dependencia, no por importancia. F2 cambia la cifra, así que todo lo que
se escriba antes de resolverlo hay que reescribirlo.

---

### F1 — Unidad de conteo de inmueble a local — HECHO (2026-08-28)

El padrón agrupa por habilitación: `solicitud` (más unidad funcional) en los siete archivos
viejos y `disposicion` en el de 2025, con partida + nombre de respaldo. **El universo A
pasa de 1.176 a 1.219** y el A+B de 1.647 a 1.732.

Lo que apareció al hacerlo, y que la medición previa no veía:

- **La misma habilitación estaba publicada en dos archivos con dos identificadores.** El
  padrón 2025 republica trámites viejos; como el legacy se identifica por `solicitud` y el
  moderno por `disposicion`, el mismo local entraba dos veces. Son **59 casos del universo
  A**, que se unen cuando coinciden partida, domicilio y año y hay exactamente un grupo de
  cada lado. Por eso la cifra final es 1.219 y no los 1.280 que anticipaba el diagnóstico:
  ese cálculo sumaba los dos padrones sin cruzarlos.
- **379 solicitudes aparecen en dos archivos legacy** por el solape de años, siempre con el
  mismo domicilio. Agrupar por solicitud las une, que es lo correcto.
- **El nombre se perdía al fusionar.** Si el representante del grupo es una fila vieja sin
  nombre, ahora se completa con el del padrón 2025. Sin eso, la cobertura de nombres caía
  de 119 a 38 y `Día Argentina S.A.` aparecía con 2 bocas en vez de 17.

**Criterios de cierre, verificados.** Ningún grupo mezcla locales distintos: de 1.732
grupos, 40 contienen más de un domicilio y los 14 que cruzan dos calles son ochavas
(Cabildo 1690 / José Hernández 2412, Entre Ríos 1098 / Humberto 1º 1799). El grupo de 362
filas no es una fusión indebida: son 900 filas crudas de una sola disposición, que el
padrón 2025 publica multiplicadas por rubro × domicilio × comentario.

**El riesgo, medido.** Una panadería con dos habilitaciones sucesivas se cuenta dos veces.
La cota superior es **83 establecimientos, el 6,8 % del universo A** (81 domicilios con dos
registros del mismo patrón, 80 de ellos con una sola partida). Lista completa en
`outputs/panaderias/analisis/d9_renovaciones_candidatas.csv`; se resuelve mirándola, en F4.
Con eso, la cifra vive entre **1.136 y 1.219**.

El lector compartido expone ahora `solicitud`, `unidad_funcional`, `partida_horizontal` y
la propiedad `clave_habilitacion`, así que **cualquier rubro nuevo cuenta bien desde el
principio**; hay seis pruebas nuevas en `tests/test_fuentes_locales.py`.

---

### F2 — Separar el pan que es negocio del pan que es góndola

**Por qué.** El 23,4 % de las habilitaciones del universo declaran además un giro ajeno —
supermercado en 321 casos. Y pega más fuerte en el grupo que parecía limpio: 29,9 % de las
que declaran elaboración, contra 11,4 % de las que sólo despachan. Son los supermercados
con horno.

**Qué hacer.** Agregar al maestro una columna `giro_principal` con tres valores:

- `panaderia` — ningún otro giro en la habilitación.
- `pan_en_otro_giro` — convive con supermercado, farmacia, kiosco, estación de servicio.
- `indeterminado` — el archivo moderno, que no permite agrupar los rubros de una
  habilitación.

No borrar nada: es una columna, igual que el nivel A/B/C. La lista de giros ajenos ya está
en `scripts/panaderias/diagnostico_unidad_de_conteo.py` y hay que revisarla a mano una vez
—no toda coocurrencia es contaminación—, apoyándose en `p2_contaminacion_multirubro.csv`.

**Criterio de cierre.** Las 18 bocas de `Día Argentina S.A.` y las 2 de `Farmacia Orien
S.A.` salen etiquetadas `pan_en_otro_giro`, y una muestra de 30 casos revisados a mano
coincide con la etiqueta.

**Dependía de F1**, porque la coocurrencia de rubros se mide dentro de una habilitación.
F1 está cerrado, así que F2 se puede hacer: el maestro trae `clave_habilitacion` y el
diagnóstico de multi-rubro ya agrupa por solicitud.

---

### F3 — Decidir y publicar la cifra

**Por qué.** Del mismo padrón salen varios números: **1.219** (hoy, contando por
habilitación), **1.136** si las 83 renovaciones candidatas fueran todas el mismo local, y
uno menor todavía descontando el pan que está dentro de otro giro, que F2 va a fijar. No se
promedian: se elige.

**Qué hacer.** Una página con las tres cifras, qué mide cada una y cuál se recomienda, para
que Diego firme. La recomendación sale de para qué se va a usar: para política de fomento
al comercio de proximidad, la cifra útil es la de panadería como negocio principal.

Es decisión de Diego, no del código. **Bloquea F5.**

---

### F4 — Revisión humana de los casos de frontera

559 registros marcados `requiere_revision_manual`, más los **81 domicilios** de
`d9_renovaciones_candidatas.csv`, que son una lista aparte y más corta: decidir, en cada
uno, si son dos panaderías pegadas o una sola habilitada dos veces. No es trabajo de
máquina.

Conviene partirlo en tandas por comuna y esperar a F2, que cambia qué casos quedan
marcados.

---

### F5 — Fuentes externas, sólo si hace falta

Tres cosas que el padrón no tiene y que ninguna corrección interna va a darle:

- **Nombre.** 1.615 de 1.732 registros no lo tienen, porque el campo disponible es el
  titular y no se lee (guardrail 7). Sin nombre no hay ficha, ni mapa rotulado, ni
  verificación en campo.
- **Vigencia.** F02 son habilitaciones. Una habilitación de 2016 puede ser un local
  cerrado hace ocho años.
- **Actualidad.** El dato más nuevo del proyecto es 2024.

Orden recomendado: **OSM y Overture primero** (abiertas, publicables, sin costo, y en el
barrido de la Ciudad Overture rescató el 90 % de lo que Places descubría). Google Places
sólo después, con alcance acotado y autorización explícita por tarea, y para lo que las
abiertas no resuelvan.

No arrancar F5 antes de F3: sin la cifra decidida no se sabe contra qué universo se cruza.

---

### F6 — Per cápita

`panaderias_por_10000_hab` sale vacía en todas las salidas porque no hay tabla de población
en el proyecto. Con el censo 2022 por comuna y barrio cargado una vez, la ganan todos los
estudios de rubro. Es un CSV chico y no depende de ninguna de las fases anteriores: se
puede hacer en cualquier momento.

---

## Lo que depende de Diego

| | Qué | Bloquea |
|---|---|---|
| 1 | Firmar cuál cifra se publica (F3) | F5, y cualquier informe |
| 2 | Revisar a mano la lista de giros ajenos de F2 | F2 |
| 3 | Autorizar la consulta a fuentes externas cuando llegue F5 | F5 |
| 4 | Conseguir el censo 2022 por comuna y barrio | F6 |
| 5 | Decidir si se regenera casas de pastas | nada de panaderías |

Las acciones que exceden a este subproyecto están en
`docs/estudios_de_rubro/ACCIONES_PARA_DIEGO.md` y no se repiten acá.

## Lo que no vamos a hacer

- **Tocar el pipeline F01-F05.** El estudio lee `data/raw` y escribe en `outputs/panaderias`.
- **Leer `titulares` ni `cuits`** para conseguir nombres. El costo de no hacerlo está
  medido y aceptado; los nombres se buscan en fuentes externas.
- **Presentar el padrón como el total de panaderías de la Ciudad.** Es lo que estas fuentes
  ven.
- **Contar habilitaciones como locales activos** (guardrail 5).
