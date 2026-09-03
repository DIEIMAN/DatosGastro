# HANDOFF · Verificación de P078, mención de P103, §10 y R8 · 2026-08-06

Continúa `HANDOFF_POLOS_PARTES_Y_SONDA_PLACES_2026_08_06.md`. Rama `mercados-gastronomicos-v2`.
**Sin commit.** Ninguna cifra publicada tocada; el Atlas no se tocó.

**Google Places: 0 requests.** El reanálisis de la sonda corrió con `--solo-analisis` desde los
crudos guardados. Total de agosto sigue en **380**.

Scripts nuevos: `polos_p078_donde_caen_los_123.py`, `polos_foco_menor.py`,
`justificar_grilla_continuidad.py`.

---

## 1 · P078 · la verificación REFUTA el motivo, y la excepción no se firma

Se pidió confirmar que los 123 locales de afuera están en los intersticios entre las tres partes.
**No lo están.** La lectura se declaró antes de correr y el número cayó del otro lado.

| medida | resultado | qué decía la lectura previa |
|---|---:|---|
| **entre dos partes** | **9 de 123 · 7,3 %** | ≥ 67 % confirmaba; ≤ 33 % refutaba |
| colgando de una sola parte | 114 de 123 · 92,7 % | |
| adentro del envolvente de las tres partes | 18 de 123 · 14,6 % | apoyo |
| **adentro de R01 Palermo** | **12 de 123 · 10 %** | apoyo |
| fuera de **toda** zona publicada | 108 de 123 · 88 % | |

El control es el que cierra el argumento: **las partes sí están adentro de R01 —69 %, 48 % y
51 % de sus locales— y los sueltos están al 10 %.** Sin ese control el 10 % no se podía leer; con
él, la diferencia es del objeto medido y no del tamaño del polígono.

### Qué son entonces los 123

Un **saliente direccional**, no un borde difuso: concentración direccional R = 0,70 con rumbo
medio 36°. 102 de los 114 que cuelgan están en el cuadrante N–NE–NO; al E y al SE no hay ninguno.

Y adentro del saliente hay **tres bloques de 35, 23 y 12 locales** —70 de los 123— que son
casi-partes: el mayor se quedó a **5 locales** del mínimo de 40. Ninguno de los tres está entre
dos partes; los tres cuelgan de S1.

**No se bajó el mínimo para recuperarlos** (R3). Queda anotado cuán cerca estuvo.

### Por qué el motivo escrito era autocontradictorio

La ficha de R01 dice que entre Soho, Hollywood y Las Cañitas «hay tramos sin oferta». Si eso es
cierto, **esos tramos no tienen locales — y entonces no pueden explicar 123 locales sobrantes.**
El 21 % tenía que estar en algún lado, y locales dentro de tramos sin oferta es una contradicción.
La medición lo confirma por el otro extremo: el hueco entre S1 y S2 mide ~300 m y tiene 6 locales.

Los tramos sin oferta existen y son reales. Lo que no son es la explicación de la cobertura que
falta.

### La lectura que sí sostienen los datos, y que no es la que se iba a firmar

**P078 desborda R01.** Las tres partes son la zona publicada; el 21 % es lo que el polo
algorítmico se extiende más allá del perímetro publicado, hacia el N–NE, y el 88 % de eso no está
en ninguna zona del Atlas.

Eso puede seguir siendo motivo suficiente para aceptar las tres partes —serían tres subzonas que
cubren el 79 % del polo, con un saliente afuera del perímetro publicado—, pero **es un motivo
distinto del que se escribió, y la decisión es de Diego.** No la firmo por mi cuenta: se pidió una
verificación para cerrar, la verificación dio que no, y cambiar el motivo para sostener la misma
conclusión sería exactamente lo que R3 prohíbe con los umbrales.

**Lo que queda decidido igual:** el umbral de cobertura del 80 % no se movió y las tres partes
siguen sin estar aceptadas.

## 2 · P103 · resuelto como mención, hecho

Registrado. **No va como subzona.**

- Campo **`foco_menor`** definido en `FICHA_DE_POLO_ENRIQUECIMIENTO.md` §1.1 y en el glosario de
  `DICCIONARIO_COLUMNAS.md`. Evidencia reproducible en `borrador_polos/polos_foco_menor.csv`.
- **El campo no lleva umbral numérico, a propósito**, y el motivo quedó escrito: Belgrano —el
  precedente publicado, con tres partes— da 21,5 % de asimetría y P103 da 15,2 %. Seis puntos
  separan al caso que se publica del que se rechaza, así que **la proporción es evidencia, no
  criterio.** Decide la condición 3, que no la evalúa un algoritmo.
- Línea de ficha, para reescribir a mano:

  > «Hay un foco menor de 44 locales sobre Chacabuco, Estados Unidos e Independencia, separado del
  > cuerpo principal. No se publica como subzona: no tiene nombre de uso corriente.»

  El foco se describe **por sus calles y sin nombre**: ponerle nombre sería hacer justo lo que la
  condición 3 dice que no corresponde.

**Salvedad que viaja con la línea: las calles salen de 24 de los 44 locales** —los que tienen
dirección, el 54,5 %—. Nombran dónde está el foco; no son un recuento de oferta por calle. El dato
va en la tabla (`foco_pct_con_direccion`) y no en una nota.

## 3 · §10 reescrito · la cota del 11 %

En `ESQUEMA_BASE_GASTRONOMICA.md`. La limitación deja de ser «no sabemos si la cobertura es
pareja» y pasa a **«medimos el techo del error donde somos más débiles, y es del orden del 11 %»**,
con las **tres** calificaciones pegadas al número:

1. **cota superior, no promedio** — los 5 barrios se eligieron por ser los peores;
2. **no dice nada de vigencia** — Places descubre, no confirma;
3. **no se traslada al sur** — los 5 son del oeste y el centro, comunas **3, 10, 11 y 15**;
   ninguno de las comunas 4, 8 ni 9. Verificado contra la base, no supuesto.

Y lo que no cambia: los 121 locales no entran a la base, la licencia no es redistribuible, y la
salida sigue en `outputs/analisis_interno/`.

## 4 · R8 en la skill

`agent_skills/shared/datagastro_metodo_experimental.md` pasa de siete a **ocho reglas** y de seis
a **siete preguntas** de control. R8 con el caso del FieldMask y sus 37 requests, más el patrón
general —todo campo obligatorio se verifica no nulo en al menos una fila— y el corolario de
separar adquisición de análisis, cruzado con R5 como estándar para toda consulta paga.

Es archivo único, sin réplicas: no hay parity checker que correr.

## 5 · `material_metodo/` · 32 → **40 archivos**

Todo lo pedido, más lo que salió de esta tanda:

- **Justificación geométrica de la grilla 20–300 m**, en texto y en tabla. La ley `1/(2·√λ)` se
  verifica contra los datos: observado/predicho entre 0,69 y 0,84 —los puntos reales están siempre
  más juntos, porque la gastronomía se agrupa y Poisson supone independencia—.
  **Y un resultado que no estaba buscado:** el orden por densidad nominal y por vecino observado
  **no coinciden**, y el caso que los separa es P065. Su densidad se mide sobre una cáscara que
  incluye los vacíos de la unión, así que la subestima. Es un **control independiente de su
  encadenamiento**, por un camino distinto del de la curva de continuidad.
- **Resultado de la sonda de Places** con sus calificaciones, `places_sonda_resultado_nucleo.csv`.
- **Los 123 de P078**, las tres tablas.
- **El test de regresión del normalizador**, incluido por sus casos negativos.
- Las curvas de los 4 polos de 300+ ya estaban.

**Nivel de publicación de lo de Places, que es una decisión y conviene que se vea:** al material
—que sí está en Git— entró **sólo el agregado por barrio**, que es el nivel `agregado` de la tabla
de licencias de R6. Ningún punto, ningún `place_id`, ninguna identidad. Verificado por grep sobre
la carpeta. Los crudos y los puntos siguen en `outputs/analisis_interno/`.

---

## Trampas encontradas hoy

- **Un motivo documental puede ser autocontradictorio y sonar perfecto.** «Los tramos sin oferta
  explican el 21 % que falta» se cae sola apenas se la escribe entera: si no hay oferta, no hay
  locales que contar ahí. La verificación no descubrió un dato nuevo, descubrió que la frase no
  cerraba.
- **Un porcentaje de pertenencia no se puede leer sin el mismo porcentaje sobre un grupo de
  control.** «Sólo el 10 % de los sueltos está en R01» no significaba nada hasta saber que las
  partes están al 69 %, 48 % y 51 %. Con otro control, el mismo 10 % habría sido inocuo.
- **El mismo campo trae tres convenciones de nombre de calle** —«INDEPENDENCIA AV.», «Avenida
  Independencia», «Av. Independencia»— y sin plegarlas una calle se cuenta como dos. Apareció
  midiendo el foco de P103: Independencia figuraba dos veces y quedaba debajo de Piedras en el
  ranking. **De la familia de R8: no rompe, no avisa, devuelve dos filas plausibles donde hay una.**
  Arreglado y con cuatro casos nuevos en el test, incluido el negativo «Avellaneda», que empieza
  con «Av» y no es una avenida.
- **Un archivo llamado `places_resumen_por_barrio.csv` invita a agarrar el equivocado.** Era el
  resumen SIN filtrar por rubro —el número que mezcla universos y que el handoff anterior ya había
  descartado—. Renombrado a `places_resumen_SIN_FILTRAR_no_usar_como_faltante.csv`, y el comparable
  ahora se escribe aparte como `places_resumen_nucleo_comparable.csv`.

## Lo que espera decisión

1. **P078: si las tres partes se aceptan con el motivo NUEVO** —«las partes son R01, el 21 % es
   desborde fuera del perímetro publicado»— o no se aceptan. El motivo viejo está refutado y por
   eso no lo cerré. Es la única decisión de esta tanda que quedó abierta.
2. **Qué se hace con el saliente N–NE de P078**, que son 108 locales fuera de toda zona publicada
   y contiene un bloque de 35 que se quedó a 5 del mínimo. No es P078 y no es ninguna zona: hoy no
   tiene lugar en el mapa.
3. Un borrado chico, que no hice por la regla de confirmar: quedó
   `outputs/analisis_interno/places_sonda_barrios_2026-08/places_resumen_por_barrio.csv`, ya
   superado por los dos archivos con nombre explícito. Es regenerable y está fuera de Git.
4. Siguen de antes: R15 Devoto, R04 Puerto Madero, las tres zonas en E3, la cláusula ODbL, el visto
   de Patricia, Bares Notables contra la normativa, Foursquare.
5. **El documento extenso del método**, que lo escribe Diego con el material de §5.
