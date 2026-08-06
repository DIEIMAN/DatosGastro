# Especificación del barrido de Places · universo gastronómico, 48 barrios

**Fecha:** 5 de agosto de 2026
**Para qué:** que el barrido se pueda presupuestar y correr sin una ronda de ida y vuelta.
Es la pieza que hay que escribir de cero al adaptar `scripts/casas_pastas/` — el resto se porta.

---

## 1 · Los tipos de Places que definen el universo

Verificados contra la Tabla A de Places API (New) al 5/8/2026. Se usan como `includedType`
y también para clasificar lo que vuelve.

**Anillo núcleo** — atención al público, es lo que se compara contra el relevamiento de campo:

```
restaurant · bar · cafe · coffee_shop · pizza_restaurant · steak_house · bar_and_grill
barbecue_restaurant · fast_food_restaurant · meal_takeaway · sandwich_shop · hamburger_restaurant
ice_cream_shop · pub · wine_bar · cocktail_bar · brewpub · gastropub · diner · bistro
cafeteria · snack_bar · food_court · tea_house · juice_shop
```

**Anillo ampliado** — se releva pero se cuenta aparte, igual que en la capa documental:

```
bakery · pastry_shop · cake_shop · confectionery · dessert_shop · donut_shop
chocolate_shop · candy_store
```

**Se excluye siempre:** `meal_delivery`, `pizza_delivery` (no son local con puerta a la calle),
`grocery_store`, `supermarket`, `food_store`, `liquor_store`, `winery`, `brewery` (producción o
retail, no gastronomía de salón).

> Las cocinas nacionales (`argentinian_restaurant`, `italian_restaurant`, `sushi_restaurant`,
> y las otras ~120 de la tabla) **no hacen falta como `includedType`**: Places devuelve el tipo
> específico dentro de `places.types` y el genérico `restaurant` ya los alcanza. Pedirlas una
> por una multiplica el costo sin agregar cobertura. Sí conviene guardarlas cuando vuelven,
> porque son el insumo del campo «cocina» de las fichas.

---

## 2 · La grilla y cuántas llamadas cuesta

El límite real no es el precio, es el techo de resultados: Text Search devuelve **hasta 60 por
consulta** (tres páginas de veinte). Donde la oferta es densa, una consulta por barrio se
satura y pierde locales en silencio. Por eso se consulta por celda, no por barrio.

Grilla de **500 metros**, con dos criterios y se toma el mayor: una celda cada 0,25 km² de
superficie, y una celda cada 40 locales esperados. El universo esperado por barrio sale de las
direcciones núcleo dividido por el factor de captura medido (18,2 %).

**Resultado: 1.190 celdas para los 204 km² de la Ciudad.**

| escenario | requests base | con paginación ×3 | ¿entra en la franja gratuita? |
|---|---:|---:|---|
| Una barrida genérica (`restaurant` + `bar` + `cafe` amplio) | 1.190 | **3.570** | **sí** — 5.000/mes en Pro |
| Tres familias de query por celda | 3.570 | 10.710 | no |
| Seis familias | 7.140 | 21.420 | no |

La conclusión práctica: **una barrida completa de la Ciudad entra en el mes gratuito.** Si se
quiere más profundidad, se parte por mes o se pide presupuesto — pero conviene correr primero
la genérica, medir qué recall dio contra las 22 zonas que ya tenemos relevadas, y recién ahí
decidir si vale la pena pagar por más.

Los diez barrios más caros, por si hace falta priorizar: Palermo 128 celdas, Balvanera 65,
San Nicolás 60, Recoleta 59, Caballito 51, Belgrano 47, Almagro 42, Monserrat 40, Villa Lugano
38 y Flores 35. El detalle de los 48 está en `grilla_places_48_barrios.csv`.

> Villa Lugano aparece alto por superficie, no por densidad: 9,3 km² con 51 direcciones núcleo.
> Ahí la grilla la manda el área, y probablemente convenga bajarla a celdas de 1 km.
>
> **AVISO (5/8/2026, tarde).** Esta grilla se dimensionó para contar, y el §3 de abajo muestra que
> contar no es lo que Places hace. El CSV **no se recalculó**: sigue intacto y la decisión de
> rehacerlo es de Diego. El criterio que corresponde para descubrimiento está en
> `AVISO_GRILLA_48_BARRIOS.md`, y no es «bajar la densidad porque alcanza con muestrear»: refinar
> la celda es lo único que baja el corte del ranking.

---

## 3 · El control · CORRIDO EL 5/8/2026, Y ÉSTE ES EL RESULTADO

> **Esta sección era una expectativa y ahora es una medición.** Lo que decía antes —«si captura
> como el directorio comercial…»— quedó superado por la corrida: se conserva el propósito del
> control, se reemplaza lo que se esperaba por lo que dio. Las tres corridas que lo produjeron
> gastaron 306 requests en total.

Se corrieron las 17 zonas con cifra publicada (256 requests), una prueba de techo sobre Villa
Crespo con tres familias de consulta y refinamiento sin tope de niveles (50 requests) y dos
análisis sin red: la captura-recaptura entre las dos corridas y el cruce contra la base documental.

**Places recupera del orden del 12 % de una cifra contada a pie**, y ese 12 % es techo estructural
de la fuente, no de esa barrida: dos corridas de la misma consulta comparten el 81,6 % de sus
resultados y la segunda agregó **un** local a la primera (N̂ ≈ 77 sobre 646). Acumular corridas no
cambia el orden de magnitud. Con el denominador común —cifra publicada, el mismo que usan las
demás fuentes— Places queda por debajo de toda fuente documental que ya teníamos: mediana del
9,7 % contra el 18,1 % del padrón solo.

Ninguna de las dos ramas que este documento anticipaba se cumplió. No captura como el campo, y
tampoco es «otra fuente de escala documental»:

**Lo que Places trae NO es lo que las fuentes documentales ya tienen.** En Villa Crespo, de sus 81
puntos, 27 caen sobre una dirección del padrón núcleo (33,3 %), 26 sobre una parcela gastronómica
del Relevamiento que el padrón no tiene, y 21 no aparecen en ninguna de las dos. Medido en las 14
zonas con muestra suficiente, la porción que el padrón ya tiene va del 7,1 % al 81,8 %, con mediana
del 37,5 %: **en 11 de 14 zonas la mayor parte de lo que Places encuentra son direcciones que el
padrón no registra.**

De ahí sale el uso que le corresponde, que no es ninguno de los dos previstos:

- **no sirve para contar** —recupera el 12 % y tiene techo—;
- **no sirve como sonda de vigencia sobre lo conocido**: confirma abiertas 26 de las 233
  direcciones núcleo del padrón en Villa Crespo, el 11,2 %. Es poca base para eso;
- **sirve como fuente de descubrimiento**: aporta locales que ninguna fuente documental tiene, y
  **dónde** aporta más es en sí mismo un dato —la proporción que el padrón ya tiene mide cuán al
  día está el padrón en esa zona—.

Detalle reproducible en `generado/CRUCE_PLACES_PADRON_R08.txt` y
`generado/UNIVERSO_POR_CAPTURA_17_ZONAS.txt`.

### Lo que se probó y no funcionó

Que en Villa Crespo el solape con el padrón fuera casi exactamente el que daría el azar sugería
usar padrón × Places como captura-recaptura para estimar el universo de un barrio sin caminarlo.
**Se probó sobre las 17 zonas con predicciones escritas antes de calcular, y falla:** de las tres
zonas con conteo de campo y muestra suficiente, acierta en una (Villa Crespo, 1,09 de la cifra) y
en las otras dos se queda en 0,40 y 0,43. Las dos fuentes no son independientes en general —se
solapan más de lo que el azar daría, o sea que las dos ven a los mismos locales visibles— y el
estimador subestima. **La línea queda cerrada; no se vuelve a intentar sin una fuente nueva.**

---

## 4 · Estimación de contexto, para tener orden de magnitud

Aplicando el factor de captura medido a las 7.181 direcciones núcleo, el universo gastronómico
de la Ciudad estaría en el orden de **37.700 locales**. Es una extrapolación, no una medición:
sirve para dimensionar la grilla y para saber si un resultado de Places es plausible, no para
publicarse.

---

## 5 · Lo que no cambia

Los guardarraíles del piloto se conservan enteros: key sólo desde `GOOGLE_MAPS_API_KEY`, nunca
impresa ni commiteada; `--dry-run` por defecto; límites por corrida; salida fuera de Git; sólo
API oficial, nada de scraping. Y la publicación pasa por `google_places_publicar_sanitizado.py`:
del lado publicable van agregados por barrio y por zona, nunca el listado con nombre, dirección
o `place_id`.
