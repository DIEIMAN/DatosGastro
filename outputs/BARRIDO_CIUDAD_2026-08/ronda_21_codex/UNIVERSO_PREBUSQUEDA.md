# Ronda 21 — universo congelado antes de la búsqueda

Fecha de extracción: 2026-08-10.

Fuente leída: `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/ATLAS_V3_DOCUMENTO.md`.
Control de cantidad: `DE_ACA_AL_FINAL.md` declara 9 `probablemente abierto`, 7 `sin verificación
individual`, 3 `en conflicto entre dos fuentes` y 3 `dudoso`: 22 estados abiertos.

Este archivo se escribió antes de iniciar búsquedas web. Congela el universo y no contiene
resultados de la ronda 21.

## 1. Los veintidós estados abiertos

| id | página del atlas | establecimiento | dirección publicada | estado de entrada |
|---|---|---|---|---|
| A01 | Retiro | Bárbaro | Tres Sargentos 415 | probablemente abierto |
| A02 | Donado–Holmberg | El Bohemio | Donado 1802 | probablemente abierto |
| A03 | Donado–Holmberg | Cigaló | Holmberg 2004 | probablemente abierto |
| A04 | Flores · Avellaneda y Pasaje Ruperto Godoy | Barthalé | Ruperto Godoy 712 | probablemente abierto |
| A05 | Flores · Avellaneda y Pasaje Ruperto Godoy | Yugane | Páez 3063 | probablemente abierto |
| A06 | Mataderos | Bar Oviedo | Av. Lisandro de la Torre 2407 | probablemente abierto |
| A07 | Mataderos | Bar del Glorias | Andalgalá 1982 | probablemente abierto |
| A08 | Villa Luro | Alma y Fuego | Av. Rivadavia 10399 | probablemente abierto |
| A09 | Villa Luro | Casa Tónica | Av. Rivadavia 10101 | probablemente abierto |
| A10 | Avenida Boedo | San Antonio | Av. Juan de Garay 3602, esquina Av. Boedo | sin verificación individual |
| A11 | Villa Crespo | Alcanfor | Aguirre 949 | sin verificación individual |
| A12 | Villa Crespo | Horta | Aguirre 1080 | sin verificación individual |
| A13 | Villa Crespo | Julia | Loyola 807 | sin verificación individual |
| A14 | Villa Crespo | Trescha | Murillo 725 | sin verificación individual |
| A15 | Villa Crespo | Fico | Muñecas 775 | sin verificación individual |
| A16 | Villa Crespo | Han | Vera 966 | sin verificación individual |
| A17 | Donado–Holmberg | Chicama | Donado 1995 | en conflicto entre dos fuentes |
| A18 | Flores · Avellaneda y Pasaje Ruperto Godoy | Shabu Shabu 153 | Páez 3154 | en conflicto entre dos fuentes |
| A19 | Parque Avellaneda | La Barra del Parque | Lacarra 836 | en conflicto entre dos fuentes |
| A20 | Retiro | Confitería Saint Moritz | Esmeralda 894 | dudoso |
| A21 | Mataderos | 9 de Julio | Larrazábal 1276 | dudoso |
| A22 | Mataderos | El Cedrón | Av. Juan B. Alberdi 6101 | dudoso |

### Control de integridad de la extracción

La prosa del atlas y el cuadro 9/7/3/3 no están totalmente reconciliados. La tabla anterior es la
reconstrucción compatible con el total declarado de 22, pero se congelan también estas anomalías:

- El atlas llama `probablemente abierto` a El Puentecito en la página Barracas · Iriarte,
  California y Vieytes, pero ese caso no entra en el total declarado de nueve.
- El Bohemio queda agrupado como `probablemente abierto` con Cigaló, aunque su pieza citada es de
  diciembre de 2024 y la propia regla del atlas manda `dudoso` cuando no hay nada posterior a 180
  días.
- Cimino R (Donado 1919) conserva sólo una pieza de febrero de 2022, pero la prosa no le imprime la
  palabra `dudoso`.
- Varias frases `sin verificación individual` quedaron desactualizadas después de verificaciones
  humanas registradas en `catalogo_90_estado_final.csv`. Para no reabrir casos ya resueltos, el
  universo de siete retiene San Antonio y los seis establecimientos de Villa Crespo que siguen sin
  pieza individual en la versión de trabajo.

Estas anomalías no se corregirán en la fuente. La búsqueda cubrirá también El Puentecito y Cimino R
como controles, en filas separadas y sin alterar el universo 22.

## 2. Los dieciséis bloques “Lo que falta” que contienen verificar/reverificar

| id | página del atlas | pedido literal o abreviado | establecimiento(s) y dirección(es) extraídos |
|---|---|---|---|
| P01 | Avenida Boedo | verificar Café Margot y San Antonio; revisar Homero Manzi | Café Margot, Av. Boedo 857; San Antonio, Av. Juan de Garay 3602; Esquina Homero Manzi, Av. San Juan 3601 |
| P02 | Caballito | verificar Mercado del Progreso | Mercado del Progreso, Av. Rivadavia 5430 |
| P03 | Devoto | verificar Café de García | Café de García, Sanabria 3302 |
| P04 | Villa Urquiza | verificar Café de la U | Café de la U, Av. Triunvirato 4801 |
| P05 | Federico Lacroze | verificar que el contorno nuevo contenga al viejo | no pide un establecimiento: control geométrico |
| P06 | Palermo | verificar los cinco MICHELIN sin fecha propia | Don Julio, Guatemala 4699; Crizia, Fitz Roy 1819; CoChinChina, Armenia 1540; A Fuego Fuerte, Bonpland 1670; Mengano, José Antonio Cabrera 5172 |
| P07 | La Paternal | verificar MN Santa Inés | MN Santa Inés, Ávalos 360 |
| P08 | Retiro | verificar Bárbaro y Confitería Saint Moritz | Bárbaro, Tres Sargentos 415; Confitería Saint Moritz, Esmeralda 894 |
| P09 | Av. Montes de Oca | verificar El Puentecito y resolver dirección | El Puentecito, Vieytes 1895 / Luján 2101 |
| P10 | La Boca · Almirante Brown y Necochea | verificar reapertura de Gennarino | Gennarino, esquina de Suárez y Necochea; el atlas no publica altura |
| P11 | La Boca · Caminito y Vuelta de Rocha | verificar Genovés | Genovés, Brandsen 923 |
| P12 | Almagro | verificar los establecimientos nuevos | El Símbolo, Av. Corrientes 3787; La Orquídea, Av. Corrientes 4101; Pin Pun, Av. Corrientes 3954 |
| P13 | Flores · Avellaneda y Pasaje Ruperto Godoy | verificar la vigencia de los once | Barthalé, Ruperto Godoy 712; Bulmat, Ruperto Godoy 731; Karaoke W, Ruperto Godoy 761; Pan Moa, Ruperto Godoy 763; Dashimaki, Ruperto Godoy 770; Maum, Felipe Vallese 3135; Makarios, Felipe Vallese 3130; Pulpería Norte, Felipe Vallese 3123; Yugane, Páez 3063; Shabu Shabu 153, Páez 3154; Ichiban, sin dirección publicada en la página |
| P14 | Monte Castro | verificar la continuidad sobre el tramo | no pide un establecimiento: relevamiento del tramo Álvarez Jonte 4400–5300 |
| P15 | Villa Luro | reverificar los tres que quedaron en 2023 | Estación de Milanesas, Acassuso 5202; García Restaurante, García de Cossio 5727; Mich Bar, Basualdo 103 |
| P16 | Villa Ortúzar | reverificar cervecerías de 2017 y cuatro locales de 2021 | Cervecería Charlone, Freire 745; Gallo Negro, Donado 1851; Simona, Av. Álvarez Thomas 661; Cullen Henderson, Av. Álvarez Thomas 1106; Kopem, Av. Álvarez Thomas 1700; F4 Esquina, Cnel. Manuel Roseti 1596; Tía Meche, Bauness 1302; Cantina y Teatro Tai, Charlone 1752; Suculentas, Heredia 499; Curva, Caldas 1596 |

### Control de integridad de los dieciséis

El conteo de dieciséis coincide exactamente con los bloques que contienen la cadena
`verificar`/`reverificar`. Dos de ellos —P05 y P14— no piden verificar un establecimiento, sino
geometría o continuidad territorial. Se conservan porque explican el número dieciséis y se marcarán
como `no resoluble por investigación documental de establecimiento`.

