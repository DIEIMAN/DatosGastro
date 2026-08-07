# HANDOFF · Ronda 3 · la vía B por presencia, la vía D con cuatro estados y el norte · 2026-08-07

Continúa `HANDOFF_POLOS_RONDA_2_EVIDENCIA_2026_08_07.md` (misma fecha, ronda anterior). Rama
`mercados-gastronomicos-v2`. **Google Places: 0 requests.** USIG sí. Ninguna geometría publicada,
ficha ni cartografía tocada. Lectura previa escrita antes de correr:
`outputs/BARRIDO_CIUDAD_2026-08/seis_vias/LECTURA_PREVIA_RONDA_3.md`.

**El informe completo está en `outputs/BARRIDO_CIUDAD_2026-08/seis_vias/INFORME_RONDA_3.md`.**

---

## Lo primero, porque revierte a la ronda anterior

**P008 Barracas no está cerrada.** La ronda 2 la bajó sobre un `no` de una sola fuente. Los
Laureles pasa a `en_disputa` —dos medios nacionales publican el mismo día que cerró y que no— y
P008 queda **pendiente**, que no es abrir ni cerrar.

Y la regla que sale de ahí, la vía B por **presencia** y no por trayectoria, cambia el número más
grande de la matriz: **vía B 43 → 7 de 94**, con 37 pendientes. Esas 43 no se perdieron: nunca
existieron. La regla vieja contaba como «abre» 212 hitos que nadie miró.

---

## Scripts nuevos

| script | qué hace |
|---|---|
| `hitos_ronda_3_vigencia.py` | vigencia con cinco valores, las 12 altas, SHA-256 de los catálogos |
| `enclaves_ronda_3.py` | los 15 enclaves → geometría donde la fuente la permite; poligoniza E01 |
| `polos_seis_vias_r3.py` | recomputa **sólo** B y D; A, C y F se leen de la ronda 2 sin recalcular |
| `norte_y_liniers_ronda_3.py` | IDECBA vs bolivianos, viaducto de Núñez, R18, las seis del norte |
| `entur_x_via_e.py` | Tarea 5 con los dos controles y la prueba de H2 |
| `usig_bordes_ronda_3.py` | los cinco bordes, con control sobre La Academia |

Los archivos de la ronda 2 quedan **intactos**; la ronda 3 escribe con sufijo `_r3`.

---

## Los ocho resultados

1. **Vía B: 7 abren, 37 pendientes, 48 sin hitos, 1 en disputa, 0 extinguidas.** `sin_verificar` es
   mayoría, pero de las filas **que tienen hitos**: 36 de 44, el 82 %. Las otras 48 son `sin_hitos`,
   un sexto valor que la decisión no cubría y que hay que confirmar.
2. **Vía D: 12 abiertas y 80 `no_medida`.** Lo importante no es el 12: las 87 filas que decían `no`
   ahora dicen «no lo medimos», que es lo que eran. Enclaves cruzables: 4 → 7.
3. **El Abasto se mide.** E01 poligonizado: 3 tramos, 506 m, 28,8 ha. PG013 pasa de cerrada a
   abierta por E01 y E05. `es_normativa = no`: es una placa de 2012, no una norma.
4. **Un bicho en la geometría de Liniers.** El callejero tiene **dos** Ramón Falcón, y la receta de
   la ronda 1 usaba la que no es: E07 estaba 900 números al oeste del Mercado Andino. Corregido —
   el eje pasa de 3.381 m a 4.981 m.
5. **La convergencia del IDECBA es de área, no de puerta.** 0 de 5 locales bolivianos están sobre
   Ramón Falcón; 3 de 5 caen dentro de 150 m. Lo que sí se sostiene con número: el tramo del IDECBA
   tiene **189 locales/km contra 58** en el resto de la calle.
6. **Núñez: mi predicción se cayó.** Dije que 16,6 locales/km no forman cadena; el clustering
   encontró **dos polos con el 85 % y el 95 % de sus locales dentro del corredor**. Los 58 de la
   nota son *inaugurados*; la base cuenta todo lo que hay. La cifra de prensa sigue sin entrar a
   ninguna columna.
7. **ENTUR × vía E: rho = +0,252, dentro del rango predicho, y aun así no hay señal.** El control de
   permutación falla: el percentil 95 del nulo es +0,361 y el p empírico 0,119. **La razón no entra
   a la matriz.** H2 se cumple en el cuadrante emergente (2025) y falla en el de declive (2026),
   que además tiene dos zonas y una sin fuente.
8. **Circulan tres contenidos del catálogo de Notables, no dos.** El PDF en disco desde el
   03/08/2026 trae **90 entradas y las doce altas**, y su hoja de firmas está fechada el **26 de
   febrero de 2026**. La URL sirve hoy 88 con siete. Si un documento de febrero ya las lista, «alta
   del 3 de agosto» no describe el acto declaratorio — y la resolución sigue sin localizarse.

---

## Los bordes, que USIG contestó todos

Control: **La Academia → Balvanera, Comuna 3**, contra la Comuna 5 del catálogo. Pasa.

- **La Escuela → Núñez, Comuna 13.** El catálogo tenía razón; La Nación no. La única vía B de Núñez
  cuenta para Núñez.
- **La Mezzetta → Villa Ortúzar, Comuna 15.** La Pizzería Emblemática cuenta para Z44, no para R09.
- **Vereda Adentro → Núñez.** **Corte Comedor → Belgrano** (Time Out se equivoca).
- **Y la quinta pregunta estaba mal planteada:** «¿Flores o Floresta?» presupone dos barrios. Las
  tres direcciones caen en **tres**: Av. Avellaneda 3069 → Flores (C7), Cuenca 954 → **Villa Santa
  Rita (C11)**, Campana 685 → Floresta (C10). E06 hay que poligonizarlo por altura, no por nombre.

---

## Trampas encontradas hoy

- **El callejero puede tener dos calles con el mismo apellido.** «FALCON, RAMON L.,CNEL.» (1.728 m
  en Liniers, alturas hasta 7300) y «FALCON, RAMON L.,CNEL. AV.» (128 m, alturas 5902-6000). Elegir
  la de la variante «AV.» no da error: da un enclave en el lugar equivocado.
- **Y puede invertir el nombre.** «Jean Jaurès» es `JAURES, JEAN`. Escribirlo como se lee lo pierde
  en silencio.
- **Un rango de alturas puede ser más corto que la cuadra.** Argerich 809-843 son 34 números; ningún
  centroide de segmento cae adentro y el tramo sale vacío. Se toma el segmento que contiene a las
  dos cabeceras y queda dicho.
- **«Sin cabecera entra entera» puede inflar.** La regla existe para no inventar cortes, no para
  ignorar los que la fuente da. «Jean Jaurès al 600» tiene cabecera; leerlo como si no la tuviera
  llevaba E01 de 28,8 a 66,3 ha.
- **La fecha de actualización de una nota no es la fecha de sus datos**, y eso hay que aplicarlo al
  parsear: las fuentes «act. 2025» se contaron por su año original, o H2 se habría medido sobre
  añadas infladas.
- **«Dudoso» no es un solo estado.** «El catálogo no acredita apertura» vale para los 90 y es
  `sin_verificar`. `dudosa` se reserva para donde hay motivo positivo para dudar.

---

## Lo que espera decisión

1. **El sexto valor de la vía B** (`sin_hitos`, 48 de 92 filas) y **el quinto de la vía D**
   (`enclave_en_formacion`, E15): confirmarlos o plegarlos.
2. **E07 Liniers reconstruido** sobre la calle correcta: revisar el polígono, y decidir si se
   recuperan las cinco fuentes accesibles que cerrarían el cuadrante.
3. **R18**: redibujar o no. Contiene al clúster documentado (98 % de su envolvente) y es cuatro
   veces más grande. Las 25 direcciones del direccionario de La Nación cambiarían la cuenta; hay 7.
4. **R03 San Telmo queda con cero vías abiertas** — sus A, C y F ya daban `no` y B/D están
   pendientes. Y el Mercado de San Telmo sigue 64 m afuera de R03.
5. **La resolución de las 12 altas**, contra un anexo firmado el 26/02/2026 que ya las lista.
6. **Verificar vigencia sobre los 207 `sin_verificar`**, priorizando los hitos únicos de su fila.
7. **E06 por altura de puerta**, ahora que se sabe que cruza tres barrios y tres comunas.
8. Sigue de antes: los 48 ejes comerciales a geometría, las 39 filas que superponen territorio,
   `Ultramarinos` sin geocodificar, `Mercado San Nicolás` y `Smart Plaza Parque Patricios` sin
   dirección, el saliente N–NE, R01 en la V3 con el 47,7 %, la cláusula ODbL, el visto de Patricia,
   Foursquare y el documento extenso del método.

**Y una que nace hoy:** la serie Z (Z23–Z46, 24 zonas candidatas del relevamiento documental) no
tiene lugar en la matriz del repositorio. Se las mide de a una cuando hace falta, pero no hay
tabla que las contenga.
