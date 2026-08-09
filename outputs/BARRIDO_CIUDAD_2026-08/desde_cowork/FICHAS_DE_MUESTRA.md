# Cuatro fichas de muestra

**6 de agosto de 2026** · Escritas a mano para fijar el molde antes de generar las 124. Se
eligieron cuatro casos distintos a propósito: uno grande con nombre de uso corriente, uno con
nombre normativo pendiente de verificar, uno del sur sin nombre propio, y uno con un límite de
lectura fuerte.

**Es más barato corregir el molde que 124 fichas.**

---

## 1 · Palermo Soho

*Nombre de uso corriente*

**Palermo** (719 locales) · **Villa Crespo** (9) · Comunas 14 y 15

| | |
|---|---|
| Locales relevados | **728** |
| Superficie | 92,4 ha |
| Densidad | 7,9 locales/ha · **concentración** |
| Ejes | Av. Raúl Scalabrini Ortiz · Armenia · Costa Rica · Gorriti · Honduras · Malabia |

Es la concentración más grande de la Ciudad. Ocupa la mitad sur de Palermo Viejo, al sur de la
Av. Juan B. Justo, con núcleo en la Plaza Julio Cortázar —Serrano y Honduras— y la Plaza
Inmigrantes de Armenia.

**Hitos** · Don Julio (Guatemala 4699), una Estrella MICHELIN y tercero en Latin America's 50
Best. El Preferido de Palermo. Tres Monos, décimo en The World's 50 Best Bars.

**Límites de lectura** · El 43 % de sus locales trae dirección, así que el ranking de ejes
describe bien la zona pero no la agota. La concentración vecina más cercana está a 75 metros: el
borde norte de este polo y el sur del siguiente son una decisión, no una línea del terreno.

---

## 2 · Distrito Tecnológico (Parque Patricios)

*Nombre reconocido — Ley 2972/2008, prorrogada por Ley 6392/2020*

**Parque Patricios** (130) · **Nueva Pompeya** (37) · **Boedo** (22) · Comunas 4 y 5

| | |
|---|---|
| Locales relevados | **189** |
| Superficie | 100,8 ha |
| Densidad | 1,9 locales/ha · **concentración extendida** |
| Ejes | Av. Caseros · Av. Chiclana · La Rioja · Almafuerte · Zavaleta · Patagones |

Actividad tendida sobre la Av. Caseros, que es el eje comercial interno del distrito. La
concentración excede el barrio: un quinto de sus locales está en Nueva Pompeya y otro tanto en
Boedo.

**Límites de lectura** · Es una concentración extendida, no compacta: 1,9 locales por hectárea
sobre cien hectáreas. Se la lee como corredor, no como polo con centro. *El nombre está sujeto a
la verificación de contenencia contra el perímetro de la Ley 2972.*

---

## 3 · Av. Larrazábal y Av. Riestra (Villa Lugano)°

*Nombre propuesto*

**Villa Lugano** (100) · Comuna 8

| | |
|---|---|
| Locales relevados | **100** |
| Superficie | 100,9 ha |
| Densidad | 1,0 locales/ha · **concentración extendida** |
| Ejes | Murguiondo · Av. Riestra · Argentina · Av. Larrazábal · Somellera · Delfín Gallo |

Cien locales repartidos sobre cien hectáreas, entre las avenidas Larrazábal y Riestra. Es una de
las once concentraciones de las comunas 8 y 9.

**Límites de lectura** · Para esta zona no se identificó ninguna denominación de uso corriente:
«Larrazábal» y «el centro de Lugano» son nombres de calle, no de zona. El nombre que lleva es
propuesto. La concentración más cercana está a 292 metros, así que no hay ambigüedad de borde.
*Podría corresponder al Distrito del Deporte (Ley 5235), pendiente de verificación.*

---

## 4 · La Isla (La Paternal)

*Nombre de uso corriente*

**Villa Gral. Mitre** (61) · **Villa Crespo** (47) · **La Paternal** (37) · **Caballito** (16) ·
Comunas 6, 11 y 15

| | |
|---|---|
| Locales relevados | **161** |
| Superficie | 91,6 ha |
| Densidad | 1,8 locales/ha · **concentración extendida** |
| Ejes | Av. San Martín · Av. Juan B. Justo · Av. Donato Álvarez · Camarones · Darwin |

El triángulo entre las avenidas Warnes, San Martín y Juan B. Justo. Cae parcialmente dentro del
Distrito Audiovisual (Ley 3876).

**Límites de lectura** · Cruza cuatro barrios y tres comunas: no aparece completa en ningún
informe comunal. La cobertura de la base en La Paternal está en el percentil diez de la Ciudad, de
modo que **sobre la extensión exacta de esta concentración no se concluye nada** — lo que se
afirma es lo que se encontró, no su límite. Existe otra «La Isla» en Recoleta; no son la misma.

---

# Notas sobre el molde

**Lo que funciona y conviene conservar:**

- El orden fijo: encabezado, tabla, un párrafo de descripción, hitos si los hay, límites de
  lectura siempre.
- **La ficha se lee en treinta segundos** y el párrafo de límites es corto. Si crece más de tres
  líneas, es que el polo tiene un problema y hay que mirarlo aparte.
- El `°` no necesita explicación en la ficha: se explica una vez al abrir la sección.

**Dos ajustes que salieron de escribirlas:**

1. **La clase de densidad y la cifra van juntas en la misma línea**, no en campos separados.
   «1,9 locales/ha · concentración extendida» se lee de un saque; en dos filas, no.
2. **`distancia_al_corte` no va en la ficha.** Es un número que sólo significa algo para quien
   conoce el método. Va en la capa de datos, y en la ficha entra únicamente como frase cuando el
   polo está al filo: *«este polo está al filo del corte de clase»*.

**Un campo que hay que agregar:** *distancia a la concentración más cercana*. Apareció escribiendo
la ficha 1 y la 3 y las dos veces resultó ser lo que explicaba el borde. Ya está en
`POLOS_PARA_NOMBRAR.csv` como `d_al_vecino_entre_puntos_m`.

---

# Y un hallazgo que salió de escribir las fichas

**El normalizador de nombres de calle no colapsa las variantes de abreviatura, y eso está
ensuciando el campo de ejes — que es un campo que se publica.**

En **nueve de los 124 polos, la misma calle aparece dos o tres veces en su propio top-6**:

| polo | lo que aparece |
|---|---|
| P048, P071 | `Cap Ramon Freire` **y** `Capitan Ramon Freire` |
| P015 | `Barco Centenera`, `Barco Del Centenera` **y** `Del Barco Centenera` |
| P001 | `Costanera Rafael Obligado`, `Costanera Obligado Rafael`, `Rafael Obligado Costanera` **y** `Costanera Rafael Obligado S/N` |
| P022 | `Doctor Ricardo Balbin` **y** `Ricardo Balbin` |
| P047 | `Doctor Juan F Aranguren` **y** `Juan F Aranguren` |
| P050 | `Doctor Honorio Pueyrredon` **y** `Honorio Pueyrredon` |
| P028 | `E Mosconi` **y** `Mosconi` |
| P072-1 | `Juana Azurduy` **y** `Azurduy Juana` |

Y hay una segunda familia que ese conteo **no** detecta, porque no es abreviatura de título sino
de nombre de pila: **`Juan B Justo` y `Juan Bautista Justo`** conviven en el top-6 de P043, y
**`Jose G Artigas` y `Jose Gervasio Artigas`** en el de P036 y P023.

**Es el cuarto caso de la misma familia en tres días** —`esq` adentro de «Esquiú», «INDEPENDENCIA
AV.», «VEGA, NICETO, Cnel. AV.»— y todos fallan igual: **en silencio**. Acá el efecto es doble:
parte el conteo de una calle en dos, y le roba un lugar del ranking a otra calle que sí debería
aparecer.

Conviene arreglarlo **antes** de generar las 124 fichas, porque el campo de ejes se publica tal
cual. Y conviene que el arreglo salga del inventario de variantes que ya está corrido
—`inventario_nombres_de_calle.csv`— y no de parchear estos ocho casos: parchear los casos que
alguien vio es exactamente lo que dejó pasar los tres anteriores.
