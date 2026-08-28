# Para Claude Code / Codex · rehacer la familia «corredor»

Trabajás dentro de `C:\proyectos\Gastronomia\DataGastro`. Todo lo que necesitás ya está medido y
escrito; falta una sola cosa, y es la que más le importa al área.

## El problema, en una línea

Un corredor **no se mide por densidad de manzana**. Se mide por **intensidad de frente sobre la
avenida**: cuántos locales hay por cada 100 metros de avenida, contando las dos veredas.

La vara de concentración por manzana —que es correcta para núcleos y para polos de varias piezas—
aplicada a corredores los rompe: de 10 corredores, sólo 3 conservan su eje. Un corredor es angosto
por definición, así que su entorno de 150 metros siempre incluye manzanas residenciales y la
densidad le da baja aunque la avenida esté llena.

## Lo que ya está hecho y no hay que rehacer

| archivo | qué es |
|---|---|
| `outputs/BARRIDO_CIUDAD_2026-08/insumos_ciudad/manzanas.geojson` | 12.640 manzanas catastrales |
| `outputs/BARRIDO_CIUDAD_2026-08/insumos_ciudad/callejero.geojson` | 31.961 tramos con nombre, tipo y alturas |
| `outputs/BARRIDO_CIUDAD_2026-08/geometria_manzanas/unidades.geojson` | 12.944 unidades atómicas: la manzana donde es una cuadra, la cara del callejero donde es un predio |
| `outputs/BARRIDO_CIUDAD_2026-08/base/local_manzana.csv` | los 27.727 locales con su manzana, barrio y comuna, verificado |
| `desde_cowork/corredores_ciudad.csv` + `.geojson` | **163 tramos de avenida con oferta sostenida**, con eje, extremos, largo, locales y locales/100 m |

## Lo que hay que hacer

**1 · Redefinir el corredor sobre el eje.**
Un corredor es un tramo continuo de avenida donde la intensidad se sostiene por encima del piso.
Parámetros actuales, todos discutibles y todos en un solo lugar del código:

```
ANCHO   = 55 m a cada lado del eje      # la vereda y su contrafrente
PASO    = 50 m                          # se camina la avenida de 50 en 50
VENTANA = 300 m                         # la intensidad se promedia, no se mide cuadra a cuadra
PISO    = 2,0 locales por cada 100 m    # el umbral
HUECO   = 250 m                         # un bache mayor corta el corredor
LARGO   = 400 m mínimo                  # menos que eso es una esquina, no un corredor
```

**2 · El ancho del corredor son las manzanas que dan al eje**, las dos veredas, desde la primera
hasta la última del tramo, sin cortar en el medio. Eso ya está implementado en `armar_corredor`;
lo que hay que sacarle es el filtro por densidad de manzana.

**3 · Los extremos.** El tramo devuelve `desde` y `hasta` cruzando contra el callejero. Hay dos
casos mal resueltos y son a mano:
- **Av. de Mayo** devuelve «de Av. Rivadavia a Av. Rivadavia» porque corre paralela a Rivadavia.
- **Donado–Holmberg** son dos calles paralelas de la ex traza AU3: el eje es doble.

**4 · Verificación obligatoria antes de dar nada por bueno:** cada corredor tiene que poder
escribirse como *«Av. X, de A a B»* y esa frase tiene que poder caminarse. Cotejá diez contra el
callejero a mano.

## Lo que NO hay que tocar

- La asignación de locales a manzanas: está verificada contra 10.889 códigos catastrales, 100 % de
  coincidencia. No la rehagas.
- Las familias núcleo y piezas: ésas sí se miden por densidad de manzana y están bien.
- La paleta y el motor de mapas: la paleta pasó el control de daltonismo en todos los pares.

## El hallazgo que hay que resolver, y es una decisión de Diego, no tuya

**129 de los 163 tramos medidos están fuera de todo polo del atlas, y suman 7.004 locales.**
Av. Córdoba (412 locales en 7,6 km), Av. Cabildo (322), Av. Rivadavia en tres tramos (310 + 186 +
136), Av. San Juan (195), Av. Francisco Beiró (182).

No los incorpores por tu cuenta. Preparalos como propuesta, con su ficha y su frase de
delimitación, y que Diego decida cuáles entran.
