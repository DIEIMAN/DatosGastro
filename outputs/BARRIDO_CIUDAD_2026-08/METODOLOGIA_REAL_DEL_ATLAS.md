# De dónde sale cada número del Atlas

**Lectura completa del repositorio · 5 de agosto de 2026**
Reconstrucción de la cadena metodológica real, a partir de la documentación de las fases de
junio, los handoffs de julio, el paquete de expansión V4, las decisiones del Atlas V2 y las
reglas de fuentes.

---

## 1 · La cadena real, en una línea

**Datos abiertos del GCBA (F01 + F02) + consultas a Google Places, cruzados y deduplicados en
escritorio.** Eso es todo. No hay ninguna otra fuente detrás de las cifras publicadas.

Confirmado por tres vías independientes:

1. **Ningún documento del proyecto menciona trabajo de campo.** Ni visita, ni recorrido, ni
   verificación en la calle. Cero resultados en todo el corpus.
2. **El propio Atlas lo dice**, en el resumen ejecutivo: *«el conteo se hizo sobre esa base y no
   recorriendo la calle»*.
3. **«Relevamiento propio DGDGAS» es sólo una etiqueta** — un `fuente_id` en
   `build_atlas_v2.py:511-515`. No designa un método.

## 2 · El vocabulario del Atlas es una capa de traducción, y está en el código

`build_atlas_v2.py` hace sustituciones literales antes de publicar:

| en el código | en el documento publicado |
|---|---|
| `Places` | «directorio comercial en línea» |
| `F01` / `F02` | «capas administrativas» |
| `businessStatus` | «estado declarado» |
| «dependencia Places» | «dependencia del directorio comercial en línea» |

Línea 733: `(r"\bPlaces\b", "directorio comercial en línea")`.

**El «directorio comercial en línea» es Google Places.** Y las «capas administrativas» son el
padrón de habilitaciones de la AGC y el listado del Ente de Turismo.

## 3 · Cuánto pesa cada fuente en las cifras publicadas

Desglose del propio JSON canónico:

| zona | cifra | capas administrativas | Places | % Places |
|---|---:|---:|---:|---:|
| R08 Villa Crespo | 646 | 178 | 467 | **72 %** |
| R10 Caballito | 907 | 265 | 642 | **71 %** |
| R17 Villa Urquiza | 189 | (separadas, no aditivas) | 189 | **100 %** |
| R15 Devoto | 119 | (separadas, no aditivas) | 119 | **100 %** |

Y la corrida V4 tanda 1 lo confirma como patrón: la columna `dependencia_places_%` da
**60,4 % a 68,8 %** en los universos combinados, y 100 % en los universos Places puros, con
`riesgo_artificial = ALTO` marcado en las cuatro zonas para el universo Places solo.

## 4 · Lo que esto corrige de lo que yo venía afirmando

Tres cosas, y las tres son mías.

**«No hay atajo, hay que caminar» era falso.** Nunca hubo campo. El bottleneck que le describí
a la Dirección no existe.

**El factor de captura que construí es parcialmente circular.** Comparé Places-hoy contra
cifras que son 60–72 % Places-de-julio. No es «una fuente contra varias»: es la misma fuente,
consultada con dos diseños distintos.

**Y por eso la conclusión «Places no sustituye el relevamiento» no significa lo que dije.** Lo
que en realidad muestra es que **nuestro diseño de consulta rinde mucho menos que el de julio**.

## 5 · Los números no cierran entre corridas, y ahí está la clave

| zona | V4 tanda 1 (corte 12-07) | ficha publicada (cita V4_4) |
|---|---|---|
| Z01 Villa Crespo | 455 = 179 admin + **276 Places** | 646 = 178 admin + **467 Places** + 1 |
| Z03 Caballito | 669 = 265 + **404** | 907 = 265 + **642** |
| Z02 Chacarita | 337 | 327 |
| Z04 Blvd. Caseros | 64 | 66 |

Entre una corrida y la otra, **Places pasó de 276 a 467 en Villa Crespo, sin cambiar la fuente**.
La carpeta que cita la ficha se llama `tanda1_saturaciones_v4_4`: fue una corrida hecha
específicamente para resolver saturaciones, es decir, para partir consultas saturadas en
consultas más finas.

**Eso es exactamente el mecanismo que el repositorio describió ayer**: el límite es un corte de
profundidad, y bajarlo es diseño de consulta. Julio lo bajó. Nosotros no.

Y hay que ser preciso sobre la magnitud: **los 81 puntos de nuestra prueba son sólo del anillo
núcleo, y no está establecido que los 467 de julio tengan el mismo filtro de rubro.** El gap
real puede ser bastante menor que 5,8×. Es lo primero que hay que medir.

## 6 · El diseño de julio, hasta donde está documentado

No hay un documento de diseño de consulta. Se reconstruye de las fichas:

- **Red de centros con radio**, no grilla — R19: «5 centros, radio 250 m» y «7 centros,
  radio 225 m»; R21: «22 centros, radio 300 m»; R22 sí usó «grilla neutral 600 m».
- **Desagregación por categoría** además de por centro — «consultas de categoría restaurante»,
  «category-split».
- **Tope de 20 resultados por consulta**, no 60. Eso indica la API vieja, no Text Search nuevo.
- **Volumen**: R21 llegó a 110 consultas, R22 a 70, R19 a 60. Nosotros hicimos 50 requests para
  17 zonas.

## 7 · Cinco cosas que hay que verificar, por orden de consecuencia

### 7.1 · Places está publicado bajo otro nombre, contra una regla del propio proyecto

`FASE_5_AUDITORIA_ESTADO_INFO_MAPAS.md`, 30 de junio, regla declarada vigente:

> *«Decidir Google Places: mantener como validación experimental interna, no fuente pública
> principal (regla vigente).»*

Y `PROTECTED_SURFACES.yaml` lo lista entre lo prohibido. Sin embargo, el Atlas de julio publica
cifras que son 60–72 % Places, bajo el nombre «directorio comercial en línea».

**Puede haber una decisión posterior que levante esa regla** — el proyecto tiene ese patrón
documentado («DEC-06 queda SUPERADA POR DEC-10»). Pero en lo que leí no aparece. Hay que
buscarla. Si no existe, es una inconsistencia institucional que conviene resolver antes de que
el documento avance, no después.

### 7.2 · La corrida que produjo las cifras está marcada como no adoptada

El paquete V4 tanda 1 dice `caracter: EXPERIMENTAL_NO_OFICIAL` y `adopcion_institucional: NO`
en las cuatro zonas. Las cifras de esas cuatro zonas —646, 327, 907, 66— se publican en el
Atlas como `naturaleza: exacta`.

La ficha cita V4_4, que es un paquete posterior y que no pude leer. **Puede tener otro estado
de adopción.** Hay que verificarlo.

### 7.3 · Las cotas «al menos» descansan en saturaciones muy grandes

R12 Centro: *«79/326 combinaciones (24,2 %) alcanzaron el máximo de 20; de categoría restaurante
51/64 saturadas»*. Es decir, más de la mitad de las consultas de restaurante en el Centro
tocaron el techo.

El «≥797» es correcto como cota inferior, pero la distancia al número real puede ser enorme, y
hoy no está acotada. Resolver esas saturaciones —partir esas consultas— probablemente mueva
esa cifra mucho.

### 7.4 · Cuatro zonas que la Fase 5 había dejado afuera aparecen con cifra

Avenida Boedo, Federico Lacroze, Villa Pueyrredón y García del Río fueron clasificadas en la
Fase 5 para no incluir, y están en el Atlas con número. Puede ser una decisión posterior
legítima; no encontré dónde se tomó.

### 7.5 · Los cuatro grupos del resumen ejecutivo pueden no medir lo que dicen

El Atlas agrupa las zonas por método: relevamiento propio, directorio comercial, mínimo
relevado, sin conteo. Pero si la diferencia entre Villa Crespo (646) y Villa Urquiza (189) es
sobre todo **cuánto se consultó** —Villa Crespo pasó por una corrida de resolución de
saturaciones, Villa Urquiza por una extracción simple— entonces los grupos separan intensidad
de consulta, no método.

Es una hipótesis. Se confirma comparando los parámetros de la corrida V4_4 contra los de la
extracción E-PLACES del 13 de julio.

---

## 8 · Lo que NO hay que hacer todavía

- **No mandar la consulta a la AGC.** El hallazgo de los lotes replicados sigue siendo válido y
  bien probado, pero conviene resolver primero lo de arriba: no es buen momento para abrir una
  conversación entre organismos.
- **No correr más Places.** Primero medir contra los datos de julio, que ya están en disco.
- **No usar la nota de una página que dejé para la Dirección.** Tiene metida la lectura de
  «relevamiento propio = campo». La reescribo cuando esto esté verificado.
- **No tocar el Atlas publicado.** Está sellado y con Patricia. Nada de lo de acá cambia una
  cifra: cambia lo que sabemos sobre cómo se produjeron.

## 9 · Lo que sí queda firme

- La capa homogénea de los 48 barrios y las cinco reglas de conteo. No dependen de nada de esto.
- El hallazgo de los lotes replicados del padrón, con su prueba catastral.
- El generador reproducible y sus controles.
- Que ninguna cifra publicada del Atlas se movió en toda la corrección editorial.
