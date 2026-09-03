# HANDOFF · La base gastronómica de la Ciudad · 2026-08-06

Continúa `HANDOFF_BASE_GASTRONOMICA_2026_08_05.md`, vigente en todo lo que no se contradiga acá.
Rama `mercados-gastronomicos-v2`. **Sin commit. Google Places: 0 requests.**

---

## Lo que cambió, en una línea

**Las tres zonas que ayer quedaron señaladas como candidatas a la primera tanda de Places
—R18, R19 y R21— se disolvieron sin gastar un request.** No les faltaba cobertura: se las estaba
comparando contra otro perímetro y otro universo de rubros.

---

## 1 · La corrección al cotejo: «13 de 17 en banda» no validaba nada, y se retiró

La lectura de ayer descansaba en una premisa falsa: que la cifra publicada de la familia
«relevamiento propio» era un conteo de campo. **No hay ningún conteo de campo en el proyecto**, y
está documentado en `METODOLOGIA_REAL_DEL_ATLAS.md` §1 y §3 con el desglose del JSON canónico:

    R08 Villa Crespo · 646 = 178 capas administrativas + 467 Google Places  (72 % Places)
    R10 Caballito    · 907 = 265 capas administrativas + 642 Google Places  (71 % Places)

Toda cifra publicada es **una consolidación de fuentes**, no una medición del territorio. La base
es una consolidación de siete. Su razón compara el tamaño de dos consolidaciones, y una base con
más fuentes tiene que dar más: donde la base supera a lo publicado, **es la ganancia esperada**.

Aplicado en `cotejar_22_zonas_base.py`:

- se retiró el conteo «N de M zonas en banda» como veredicto;
- cada familia declara ahora **qué es su cifra publicada** y si su comparación es falsable. De las
  cuatro, **sólo `minimo relevado` lo es**: su cifra está declarada como cota inferior y por eso
  tiene dirección;
- **las bandas originales se conservan escritas**, con su motivo equivocado intacto, marcadas como
  registro y no como veredicto. Borrarlas habría dejado el cuadro más prolijo y habría hecho
  desaparecer la prueba de que la expectativa era otra.

La misma premisa falsa estaba en `places_control_zonas.py` —decía «contra un conteo de campo» y
«lo que encontró caminar»—. Corregida y **reinformada con `--reinformar`, 0 requests**: el número
no se movió, lo que cambió es qué mide. Lo que ese control mide es **diseño de consulta**, porque
el 70 % de su denominador también salió de Places.

## 2 · R18, R19 y R21: era perímetro y universo, no cobertura

Script nuevo: `scripts/barrido_ciudad/diagnosticar_faltante_zonas.py` · 0 requests ·
salida en `generado/DIAGNOSTICO_FALTANTE_ZONAS.txt`.

Tres ejes estaban desalineados entre la cifra publicada y la base:

1. **La precedencia de solape.** El cotejo le aplica a la base la regla que cede la superficie
   compartida al `referencia_id` menor. **Las cifras publicadas no la usan**:
   `ANALISIS_R12_SUBUNIDADES.csv` etiqueta a C-S07 como `ETIQUETA_COMPARTIDA_CON_R18`, o sea que
   los mismos 216 establecimientos cuentan en R12 y en R18 a la vez. A R18 la regla le saca el
   64 % de su superficie y después se le pide el conteo entero.
2. **Perímetro de consulta ≠ envolvente editorial.** La cifra se contó sobre la geometría con que
   se consultó; la base, sobre el polígono editorial dibujado después.
3. **Universo de rubros.** Las corridas publicadas pidieron `restaurant, cafe, bar, bakery,
   meal_takeaway`. **`bakery` cae en el anillo ampliado**, así que comparar contra `base_nucleo`
   le descuenta a la base todas las panaderías y no se lo descuenta a la cifra publicada.

| ref | ha del cotejo | ha de consulta | razón del cotejo | razón alineada | eje dominante |
|---|---:|---:|---:|---:|---|
| **R18** Esmeralda–Paraguay | 17,2 | 50,2 (2,91×) | 0,48 | **1,64** | perímetro (94 %) |
| **R19** Federico Lacroze | 89,5 | 126,0 (1,41×) | 0,89 | **1,52** | perímetro (78 %) |
| **R21** La Paternal | 321,0 | 335,4 (1,04×) | 0,82 | **1,13** | universo de rubros (71 %) |

Las otras cuatro de la familia (R12, R13, R20, R22) nunca estuvieron por debajo.

**Consecuencia operativa: no queda ninguna zona con faltante de cobertura demostrado, y la
recomendación de correr una primera tanda de Places sobre estas tres queda sin sustento.** Si se
corre una tanda, hay que elegir el destino por otro criterio.

Y la salvedad que viaja pegada al resultado: la cifra publicada de esas zonas **también salió de
Places**. Que la base la alcance no prueba que la base esté completa; prueba que llega adonde
llegó una corrida de Places de julio.

## 3 · Wikidata, corrido y medido

Script: `scripts/barrido_ciudad/bajar_wikidata_gastro.py` · informe:
`generado/WIKIDATA_GASTRO_CIUDAD.txt` · CC0.

| | |
|---|---:|
| ítems georreferenciados en la caja de la Ciudad | 6.568 |
| gastronómicos **por tipo** | 33 |
| gastronómicos **por declaratoria** («Bar Notable») | **95** |

**La advertencia de volumen bajo era correcta; el motivo, no.** De los 95 Bares Notables, **82
están cargados como «edificio»** y no como bar o café: al catalogarlos, lo enciclopédico fue el
inmueble. Filtrar gastronomía por `P31` pierde el grueso. Es una trampa general de la fuente:
`P31` describe qué es la entidad, no qué actividad pasa adentro.

Y un hallazgo institucional incómodo: **el barrido de los 453 datasets de BA Data no devolvió
ningún dataset con la lista de Bares Notables.** Hoy el índice abierto más completo de los Bares
Notables está en Wikidata y no en el portal del Gobierno que los declaró. (Puede existir sin estar
catalogado con esa palabra; lo verificable es que el barrido no lo encontró.)

**El 97 % trae dirección postal**, así que se geocodifica con USIG y la coordenada de Wikidata no
se toca. Wikidata **no forma grupo de independencia**: no es un relevamiento, es una transcripción
hecha por voluntarios, y un local «también corroborado por Wikidata» no está más corroborado.

Tres consultas partidas y cruzadas en memoria porque la consulta natural expira: ver el docstring
del script, que documenta los tres 504 y el 431.

## 4 · Fuentes nuevas y líneas cerradas

Todo en `outputs/BARRIDO_CIUDAD_2026-08/FUENTES_RONDA_3_2026-08.md`.

**Entran, las dos como capa de cruce y NO como universo:**

- **Registro Nacional de Sociedades** (CC BY 4.0, datos al 31/07/2026, domicilio estructurado,
  CUIT, `actividad_codigo` desde diciembre 2024). Dos límites declarados: **domicilio legal ≠
  local comercial** y **no incluye monotributo**. El CUIT se usa sólo como clave de cruce en
  memoria y no se escribe en ninguna salida.
- **IGJ · Entidades constituidas** (CC BY 4.0, CABA, con tabla de domicilios aparte). Las tablas
  de autoridades y balances **no se bajan**: traen personas físicas y cifras.

**Cerradas con motivo, para que no se reabran:** GeoNames (no existe código de restaurante, bar ni
café en sus *feature codes*), Pelias/Geocode Earth, Geoapify (OSM reempaquetado), datos.gob.ar
(cero datasets), Yvera, Michelin. Who's On First se descarta como fuente pero **sus polígonos de
barrio sirven como capa base**.

**Dos advertencias operativas:** Nominatim público no se usa para geocodificar en volumen (su
política lo prohíbe expresamente; se usa USIG). Wikimapia descartada pese a ser CC BY-SA: sus
datos se trazaron sobre imágenes de Google Maps, lo que los volvería obra derivada sin licencia.

**Delivery, excluido por contrato y anotado en el README de la base** con las citas de Rappi
(5.1.G y 10.2), PedidosYa, TripAdvisor Content API y Uber Eats. El motivo no es técnico y no hay
vía licenciada: es el complemento del guardarraíl 6, que ya prohíbe el scraping.

## 5 · Enganches preparados para lo que gestiona Diego

`ESQUEMA_BASE_GASTRONOMICA.md` §11, nuevo.

- **APRA** → grupo `GCBA_AMBIENTAL`; **AGIP Ingresos Brutos** → grupo `GCBA_TRIBUTARIO`; ambos con
  lista permitida de columnas y sin montos ni categoría tributaria. Ninguno convierte un registro
  en «local activo».
- **Diccionario del Relevamiento de Usos del Suelo** → no es fuente: corrige la clasificación del
  `RUS` que ya está cargado.
- **Tabulado del Censo Económico por comuna (INDEC)** → **no entra como filas: entra como
  denominador de completitud por comuna.** Es lo que hoy falta para poder afirmar si la cobertura
  es pareja. Se agregó como límite explícito en §10: *la base no sabe todavía si su cobertura es
  pareja.*

## 6 · `E-PLACES`, limpiado — y una precisión sobre su alcance

El código interno salía crudo en el `denominador_metodo` de R14, R15, R16 y R17 porque el canon
dice `Places DEDUP_CONSERVADOR Z07 E-PLACES`, sin el «registros … con» que esperaba la regla
existente. Se agregó una regla **sólo para conducción** en `FRASES_POR_EDICION`, en el lugar del
orden donde tiene que correr.

**Precisión que conviene no perder:** ese campo **no se renderiza en ninguna página de la
conducción** —esas páginas salen de `contenido_conduccion.py`, que no consume
`denominador_metodo` ni `detalle_cuantitativo`—. Así que el `deduplicación` que también emitía
**no estaba haciendo fallar el control de vocabulario**, que corre sobre las páginas compuestas.
Lo que se arregló es el contenido, para el día que el campo se use.

`(RESUMEN_UNIVERSOS_TANDA2_V1)` **se dejó a propósito**: `escribir_trazabilidad_lenguaje()` arma
el universo de números de la ficha extrayendo dígitos de todo el texto, y sacarlo achica ese
universo y puede convertir un número legítimo en un falso «número nuevo».

**La técnica conserva `E-PLACES` en crudo, y es deliberado.** Su salida está sellada como V2.1;
cualquier regla que la tocara rompería el sello, que es la garantía de que ninguna cifra técnica
se movió. En una edición técnica un código interno es información, no ruido.

### Verificado, no afirmado

Script nuevo: `outputs/polos_gastro/ATLAS_V2/scripts/verificar_sellado_ediciones.py`.
Reconstruye el contenido público de las dos ediciones desde el canon y compara campo por campo.

- **técnica: 612 campos, 0 diferencias.** Sello intacto.
- **conducción: 17 diferencias**, las mismas 17 de ayer — las cuatro de `denominador_metodo` ya
  estaban entre ellas porque `Places` → `Google Places` ya aplicaba; lo que cambió es qué dicen.
- Nada se escribió: la reconstrucción corre con `persist=False` y los JSON congelados no se
  tocaron.

---

## Lo que espera decisión

1. **Correr o no una tanda de Places, y dónde.** Los tres candidatos de ayer se cayeron. Hoy no
   hay ninguna zona con faltante de cobertura demostrado, así que el destino habría que elegirlo
   por otro criterio —y conviene esperar el denominador del INDEC, que es lo que permitiría
   detectar dónde la cobertura es despareja.
2. **La cláusula de compartir-igual de la ODbL de OSM.** Sigue pendiente del área legal.
3. **El visto de Patricia sobre el pasaje 5**, y **regenerar o no los PDF** con la reescritura.
4. **Confirmar la lista de Bares Notables contra la normativa** antes de usarla: quien la
   transcribió a Wikidata es un voluntario, aunque la declaratoria sea un acto administrativo.
5. **Abrir o no cuenta en Foursquare** (3,3 % de Overture, baja prioridad).
6. **Mandar la nota a la AGC** — sigue pendiente.

## Lo que no se tocó

Ninguna cifra publicada. Ningún PDF regenerado. Los JSON congelados de las dos ediciones. El
pipeline público F01-F05. `PROTECTED_SURFACES.yaml`. La base (`local.csv` no se regeneró).

**Google Places: 0 requests. El total de agosto sigue en 306.**

## Trampas encontradas hoy

- **Una banda escrita antes de correr no vale si su premisa era falsa.** La disciplina de escribir
  la expectativa por adelantado protege contra mirar el número y acomodar la explicación; no
  protege contra equivocarse sobre qué es el denominador. Son dos errores distintos.
- **Comparar dos conteos sobre polígonos distintos y llamarlo cobertura.** La densidad por
  hectárea es lo único que sobrevive cuando las superficies difieren, y ponerla al lado del
  conteo hace visible el problema de inmediato.
- **El endpoint de Wikidata expira con el cierre transitivo de subclases.** Tres formas dieron 504.
  Lo que entra es pedir el árbol de clases por un lado, la caja geográfica por otro y cruzarlos en
  memoria. Y un `VALUES` de 492 clases no pasa por GET: HTTP 431.
- **`P31` de Wikidata no es un filtro temático.** Un café patrimonial está cargado como edificio.
- **Antes de afirmar que un control iba a fallar, hay que ver si el campo llega al control.**
  El `deduplicación` del `denominador_metodo` parecía un bloqueante y no lo era: la conducción no
  consume ese campo. La afirmación se corrigió en el comentario del código.
