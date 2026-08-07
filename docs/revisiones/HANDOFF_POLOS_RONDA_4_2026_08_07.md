# HANDOFF · Ronda 4 · los dos enclaves de fuente, la prioridad de verificación y las fuentes con defecto · 2026-08-07

Continúa `HANDOFF_POLOS_RONDA_3_2026_08_07.md` (misma fecha). Rama `mercados-gastronomicos-v2`.
**Google Places: 0 requests.** USIG: 37 consultas nuevas, cacheadas. Ninguna geometría publicada,
ficha ni cartografía tocada. Los archivos de la ronda 3 quedan intactos; la ronda 4 escribe `_r4`.

**El informe completo está en `outputs/BARRIDO_CIUDAD_2026-08/seis_vias/INFORME_RONDA_4.md`.**

---

## Lo primero, porque es la consecuencia no pedida

Reescribir E07 sobre la delimitación de fuente **le saca la vía D a dos filas**: PGR_P017 Liniers y
PGR_P020 **Villa Luro**. El E07 de la ronda 3 medía 4.981 m de eje y 131,7 ha porque la consigna no
daba cabeceras; llegaba hasta Villa Luro y abría una vía allá. Con el eje de 284 m que mide la
fuente, queda PGR_P021 —la fila que contiene al mercado— y se caen las dos que lo tocaban por
estiramiento. **Vía D de las 94: 12 → 10.** Las 22 zonas no se mueven.

---

## Scripts nuevos

| script | qué hace |
|---|---|
| `enclaves_ronda_4.py` | reescribe E02 y E07; geocodifica las 57 puertas; mide el radio contra las bandas |
| `hitos_prioridad_verificacion.py` | las dos listas de prioridad y el orden de ataque en tres tandas |
| `fuentes_defectos_y_vigencia_r4.py` | la capa de defectos de fuente, las marcas aplicadas y los tres estados de vigencia |
| `polos_via_D_r4.py` | recomputa **sólo** la vía D contra la geometría nueva |

Salidas nuevas en `outputs/BARRIDO_CIUDAD_2026-08/`: `seis_vias/enclaves_comunitarios_r4.*`,
`enclaves_componentes_r4.geojson`, `establecimientos_E02_E07_geo_r4.csv`,
`prioridad_verificacion_*.csv`, `seis_vias_94_filas_r4.csv`, `seis_vias_22_zonas_r4.csv`, y la
carpeta nueva `fuentes/` con `fuentes_defectos_conocidos.csv`, `fuentes_marcas_aplicadas.csv` y la
sección para la edición técnica.

---

## Los cinco resultados

1. **E07 mide 284,0 m** contra los 285 medidos con USIG (0,4 %) y los «aproximadamente 300» del
   paper (5,3 %). Coincide. Montiel afuera, Salteñería corregida, eje con transversales y no
   cuadrante. **Las 6 puertas caen 6 de 6 adentro** sin trazar las transversales: Ibarrola está a una
   cuadra y el buffer de 150 m ya las contiene. 131,7 → 15,6 ha.
2. **Barrio Chino: 49 de 51 geocodificadas.** 39 núcleo · 6 corredor · 4 afuera · 2 sin geocodificar.
   Núcleo 255,2 m contra 256. Ultramarinos **confirmado sin geocodificar**: USIG rechaza la altura
   1980 sobre Arribeños en las tres variantes, y es la única vía B candidata nueva del enclave.
3. **El corredor NO es perpendicular: 19,1°, casi paralelo.** Arribeños corre al lado de las vías y
   no las cruza. La forma no es una cruz: son dos bandas casi paralelas separadas por la traza, y el
   desborde es longitudinal. **Contra el radio:** las dos formas capturan 45 de 49 y el radio gasta
   2,7 veces más superficie (81,7 ha contra 30,7).
4. **La prioridad: 18 filas frágiles, 15 con el hito sin resolver.** Tanda A 15 + tanda B 14 = **29
   verificaciones que tocan 22 filas: 13 % del trabajo para el 50 % de las filas con hitos.** Los
   cuatro de Retiro —Tancat, Saint Moritz, Florida Garden, Plaza Bar— están en 3 filas cada uno.
5. **Cuatro fuentes con defecto estructural cargadas como capa, con 20 marcas aplicadas.** FD-01
   pega en 5 establecimientos, 8 citas de evidencia —la que más pesa es R03 San Telmo— y **6 hitos de
   cronista.com sin fecha registrada**, que quedan `pendiente_de_comprobacion`, no descartados.

---

## Trampas y precisiones de esta ronda

- **Definir el corredor con las puertas que después se clasifican contra él es circular.** Sale del
  callejero oficial: los siete cruces marcados `Tren Elevado` entre Monroe y Echeverría.
- **Un largo de calle sin recorte de barrio no dice nada.** «Ramón Falcón» son 7.150 m de punta a
  punta de la Ciudad y 1.728 m dentro de Liniers. Compararlo contra la ronda 3 exige el recorte.
- **FD-01 es dominio MÁS fecha.** R15 Villa Devoto cita «Time Out BA 24/09/2025»: misma fecha, otro
  medio. Queda en la tabla marcado como falso positivo, porque la lista de lo que se decidió no
  marcar vale tanto como la de lo marcado.
- **Y el contraejemplo:** la nota de El Cronista sobre Los Laureles se publicó 12:33 y se actualizó
  12:34. Un minuto no es re-sellado. FD-01 no dice «El Cronista no sirve».
- **`dudoso_probablemente_abierto` no existe en la capa de hitos.** Viaja partido en `vigencia` y
  `sentido_de_la_duda` para que se pliegue a `dudosa` sin perder la dirección de la duda.
- **Los tres cierres del Barrio Chino salen de la misma nota de iProfesional del 04/07/2020.** Que
  dos no tengan nada después no confirma que sigan cerrados: esa nota no vuelve a mirar.

---

## Lo que espera decisión

1. **La forma final de E02**: dos bandas casi paralelas. Construida y medida, falta firma.
2. **Los 4 «afuera»** del Barrio Chino —Ma La Tang, Shanghai Express, Gokana Omakase, Sachi—: o el
   polígono crece o se aceptan como derrame declarado.
3. **Ultramarinos**: necesita resolución de dirección, no otra fuente.
4. **La ronda de verificación documental**: tandas A y B, 29 hitos. Es la que destraba la vía B.
5. **Las seis notas de cronista.com de la capa**: registrar fecha de actualización, aplicar o
   levantar FD-01.
6. **Boca a Boca**: confirmado 207 contra 201, los dos puntos a 2,6 m. Documental, no mueve ninguna
   medición. Se verifica en campo.
7. Sigue de antes: el sexto valor `sin_hitos`, el quinto de la vía D, R18, la resolución de las 12
   altas, R03 con cero vías, E06 por altura de puerta, la serie Z sin tabla, y el arrastre de la
   ronda 3.
