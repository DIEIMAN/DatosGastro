# Base homogénea de toda la Ciudad y factor de captura de las 22 zonas

**Fecha:** 5 de agosto de 2026
**Para:** Dirección General de Desarrollo Gastronómico
**Qué es esto:** las reglas de conteo únicas que se aplican de acá en adelante, el resultado
de aplicarlas a los 48 barrios, y la medición de cuánto captura cada uno de los métodos con
los que se contaron las 22 zonas del Atlas.

---

## 1 · Por qué hizo falta

El Atlas publica veintidós números que no se pueden comparar entre sí. Eso está advertido en
el documento, pero hasta ahora era una salvedad cualitativa: se decía que los métodos eran
distintos, sin decir cuánto.

Ahora se puede decir cuánto. Y la diferencia es más grande de lo que sugiere el descargo.

---

## 2 · Las reglas de conteo

Son cinco decisiones. Valen para toda la Ciudad y para cualquier zona nueva que se incorpore.
Mientras las dos líneas de trabajo —la base documental y el relevamiento de campo— usen estas
mismas reglas, sus resultados se pueden poner uno al lado del otro.

### 2.1 · La unidad es la dirección, no la habilitación

Las 42.836 habilitaciones gastronómicas georreferenciadas de la Ciudad caen sobre **7.829
direcciones distintas**: 5,5 habilitaciones por dirección. No son 5,5 locales. Un mismo local
suele tener varios rubros habilitados a la vez —«café bar» más «casa de lunch» más «despacho
de bebidas» es la combinación clásica— y además se rehabilita cuando cambia de dueño o de
rubro.

**Contar habilitaciones sobrestima entre cuatro y seis veces.** La unidad de conteo es la
dirección normalizada.

### 2.2 · Dos anillos de rubro, y siempre se informan los dos

El filtro gastronómico actual del repositorio es ancho: incluye elaboración de masas,
panadería, y comercio minorista de helados y sándwiches sin elaboración. Eso no es lo mismo
que un local gastronómico de atención al público, que es lo que releva la Dirección en la
calle.

| anillo | categorías | direcciones en CABA |
|---|---|---:|
| **Núcleo** | Restaurante, Bar, Café, Pizzería, Parrilla, Comida al paso, Heladería | **7.181** |
| **Ampliado** | núcleo + Panadería, Pastelería, Catering | 7.826 |

El núcleo es el que se compara contra el relevamiento. El ampliado se informa al lado para que
la diferencia sea visible y no haya que confiar en la elección de rubros.

### 2.3 · Se marcan las direcciones anómalas, no se borran

324 direcciones concentran más de 20 habilitaciones cada una: entre las tres, el 46,9 % de
todos los registros. La peor tiene 360, todas con el mismo rubro, número de expediente
correlativo y fecha «No disponible». Son centros comerciales, complejos y cargas masivas del
padrón, no 360 locales.

Quedan **excluidas del conteo de direcciones y contadas aparte**, en una columna propia. No se
descartan en silencio: si una zona tiene muchas, hay que mirarla antes de publicar su número.

### 2.4 · Calidad geográfica

Se usan las 10.744 direcciones con coordenada de las 10.847 del padrón (99,1 %), todas
geocodificadas con el normalizador de USIG: 7.807 exactas a calle y altura, 2.937 de fuente
oficial. La asignación a barrio y a zona se hace por geometría —punto dentro de polígono—, no
por el campo de texto, que viene entero en «No determinado».

### 2.5 · Ventana temporal y qué significa el número

La ventana es 2015–2025 completa, tal como está publicada. **El padrón no registra bajas**:
una habilitación aprobada en 2016 sigue figurando aunque el local haya cerrado en 2018. El
número resultante es *direcciones que alguna vez tuvieron habilitación gastronómica en la
década*, no locales abiertos hoy. Es una cota superior por un lado y una cota inferior por
otro, y por eso se usa como referencia de contraste, nunca como cifra publicable por sí sola.

---

## 3 · La Ciudad completa: los 48 barrios

Aplicadas las reglas, **los 48 barrios tienen dato y ninguno queda en cero**. Los barrios que
pediste incorporar entran sin necesidad de salir a la calle:

| barrio | direcciones núcleo | direcciones ampliado | habilitaciones | f01 |
|---|---:|---:|---:|---:|
| Núñez | 121 | 129 | 1.504 | 28 |
| Saavedra | 77 | 85 | 231 | 25 |
| Coghlan | 26 | 28 | 91 | 5 |
| **La Boca** | **55** | 60 | 239 | 44 |
| Barracas | 103 | 115 | 619 | 49 |
| Parque Patricios | 87 | 94 | 318 | 37 |
| Mataderos | 92 | 106 | 325 | 34 |
| Parque Chacabuco | 72 | 86 | 335 | 15 |
| Nueva Pompeya | 52 | 67 | 154 | 12 |
| Villa Lugano | 51 | 56 | 250 | 10 |
| Parque Avellaneda | 50 | 60 | 147 | 14 |
| Villa Riachuelo | 25 | 26 | 113 | 6 |
| Villa Soldati | 11 | 15 | 22 | 2 |

### Cuánto de la Ciudad tocan hoy las 22 zonas

Cruzando las envolventes editoriales contra los polígonos de barrio: **16 barrios no reciben
ninguna de las 22 zonas** —ni un uno por ciento de su superficie— y **21 quedan por debajo del
5 %**. Del otro lado, seis barrios están cubiertos en más del 70 %: Villa Pueyrredón 92 %,
Paternal 91 %, Villa Urquiza 90 %, Villa Crespo 88 %, Villa Devoto 70 %.

Los 16 sin cobertura: Floresta, Liniers, Mataderos, Parque Avellaneda, Vélez Sarsfield,
Versalles, Villa Lugano, Villa Luro, Villa Riachuelo, Villa Santa Rita, Villa Soldati, Parque
Patricios, **Núñez**, San Cristóbal, Flores y Monte Castro.

Y aparece algo que no estaba pedido y conviene mirar: **el oeste está tan descubierto como el
sur, y es más grande.**

| barrio no cubierto por el Atlas | direcciones núcleo | habilitaciones |
|---|---:|---:|
| Flores | 248 | 1.277 |
| Liniers | 114 | 2.204 |
| Villa Del Parque | 107 | 1.003 |
| Constitución | 109 | 389 |
| Boedo (barrio completo) | 99 | 380 |

Flores con 248 direcciones tiene más base que Villa Urquiza (206), que sí tiene ficha propia
en el Atlas. Liniers, con 2.204 habilitaciones, es el cuarto barrio de la Ciudad por volumen
de trámite. Ninguno de los dos está en las 22.

El detalle completo de los 48 está en `capa_homogenea_48_barrios.csv`.

---

## 4 · El factor de captura: cuánto ve cada método

Para cada zona del Atlas se recortó la base homogénea con su envolvente editorial y se comparó
contra la cifra publicada. El cociente es el **factor de captura**: qué porcentaje del número
relevado alcanza a ver la base documental.

Si los métodos midieran lo mismo, todos los factores estarían cerca del mismo valor. No lo
están. **Se separan en dos grupos que no se tocan.**

| zona | método del Atlas | publicado | base homogénea | captura |
|---|---|---:|---:|---:|
| R15 · Devoto | directorio comercial | 119 | 139 | **116,8 %** |
| R14 · Avenida Boedo | directorio comercial | 79 | 74 | **93,7 %** |
| R17 · Villa Urquiza | directorio comercial | 189 | 173 | **91,5 %** |
| R16 · Donado–Holmberg | directorio comercial | 40 | 32 | **80,0 %** |
| R13 · Abasto | mínimo relevado | ≥314 | 180 | 57,3 % |
| R12 · Centro/Microcentro | mínimo relevado | ≥797 | 327 | 41,0 % |
| R20 · García del Río | mínimo relevado | ≥40 | 16 | 40,0 % |
| **R08 · Villa Crespo** | **relevamiento propio** | **646** | **233** | **36,1 %** |
| R22 · Villa Pueyrredón | mínimo relevado | ≥158 | 48 | 30,4 % |
| R19 · Federico Lacroze | mínimo relevado | ≥211 | 54 | 25,6 % |
| **R10 · Caballito** | **relevamiento propio** | **907** | **177** | **19,5 %** |
| **R09 · Chacarita** | **relevamiento propio** | **327** | **55** | **16,8 %** |
| R21 · La Paternal | mínimo relevado | ≥254 | 41 | 16,1 % |
| R18 · Esmeralda–Paraguay | mínimo relevado | ≥216 | 30 | 13,9 % |
| R05 · Belgrano | relevamiento anterior | 697 | 100 | 14,3 % |
| **R11 · Boulevard Caseros** | **relevamiento propio** | **66** | **5** | **7,6 %** |
| R07 · Costanera Norte | relevamiento anterior | 72 | 3 | 4,2 % |

### Lo que dice la tabla

| método | zonas | captura mediana | rango |
|---|---:|---:|---|
| Directorio comercial en línea | 4 | **92,6 %** | 80,0 – 116,8 % |
| Mínimo relevado («al menos») | 7 | 30,4 % | 13,9 – 57,3 % |
| Relevamiento propio de la Dirección | 4 | **18,2 %** | 7,6 – 36,1 % |
| Relevamiento anterior | 2 | 9,3 % | 4,2 – 14,3 % |

**Los dos métodos que el Atlas presenta como conteos difieren en un factor de cinco.** Las
cuatro zonas contadas sobre directorio comercial dan números del mismo orden que un padrón de
habilitaciones; las cuatro relevadas en la calle dan números cinco veces más grandes que ese
mismo padrón.

Los 189 locales de Villa Urquiza y los 907 de Caballito no son «dos números obtenidos de otra
manera»: son **dos escalas distintas**. Puesto de la manera más incómoda posible: si Villa
Urquiza se hubiera relevado con el método de Caballito, su número no sería 189 sino del orden
de 900. Y Devoto, con 116,8 %, es el caso más claro: el directorio comercial encontró **menos**
locales que los que tienen habilitación registrada en ese mismo perímetro.

Los cuatro grupos del resumen ejecutivo ordenan bien las zonas por método. Lo que no dicen
—y ahora sí se puede decir— es cuánto cambia el número según a qué grupo cayó cada zona.

### Un caso a mirar aparte

**R18 · Esmeralda–Paraguay** tiene 1.464 habilitaciones sobre apenas 30 direcciones núcleo, y
12 direcciones marcadas como anómalas. Es el perímetro con la relación más extrema de la
Ciudad. Antes de usar cualquier número de esa zona conviene revisar qué son esas direcciones:
es plena zona de torres y galerías del microcentro norte.

---

## 5 · Qué se propone hacer con esto

**No cambiar ninguna cifra publicada.** Las 22 quedan como están; lo que se agrega es una
columna que dice, para cada una, cuánto captura la base documental en su perímetro. El
descargo «los números no se comparan entre sí» pasa de ser una advertencia a ser un dato con
magnitud.

Para las zonas nuevas, la regla es la inversa: **primero la base homogénea, después el
relevamiento**, de modo que cada zona nazca con su factor de captura conocido en vez de
tenerlo que estimar después.

---

## Archivos

| archivo | qué tiene |
|---|---|
| `capa_homogenea_48_barrios.csv` | los 48 barrios con los cuatro indicadores y las direcciones anómalas |
| `capa_homogenea_22_zonas.csv` | lo mismo, recortado por las envolventes editoriales del Atlas |
| `factor_captura_22_zonas.csv` | la comparación contra la cifra publicada, con el método de cada zona |
