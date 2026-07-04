# Casas de Pastas / Mercados de Pastas — Informe

**DGDGAS — Dirección General de Gastronomía**
Gobierno de la Ciudad de Buenos Aires

Diagnóstico territorial del rubro casas de pastas en la Ciudad de Buenos Aires.
Padrón candidato depurado y lectura territorial.

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Objetivo y alcance](#2-objetivo-y-alcance)
3. [Metodología y fuentes](#3-metodología-y-fuentes)
4. [Caracterización general del universo](#4-caracterización-general-del-universo)
5. [Principales resultados](#5-principales-resultados)
   - 5.1. Concentración territorial (cantidad)
   - 5.2. Densidad por km²
   - 5.3. Polos del rubro
   - 5.4. Cadenas frente a casas independientes
   - 5.5. Núcleo de mayor respaldo cruzado
   - 5.6. Aporte de la revisión manual
6. [Lectura territorial](#6-lectura-territorial)
7. [Lectura institucional](#7-lectura-institucional)
8. [Aspectos a considerar](#8-aspectos-a-considerar)
9. [Próximos pasos](#9-próximos-pasos)
10. [Anexos](#10-anexos)
    - A. Metodología ampliada
    - B. Tablas completas por comuna y barrio
    - C. Casos con respaldo documental
    - D. Detalle de cadenas
    - E. Limitaciones metodológicas

---

## 1. Resumen ejecutivo

Este informe dimensiona el universo probable de **casas de pastas** en la Ciudad de Buenos Aires y describe cómo se distribuye en el territorio. No es un censo ni un padrón oficial: es una **base analítica candidata**, construida para orientar validaciones y decisiones territoriales, que no reemplaza al registro oficial.

El resultado, tras cruzar fuentes y revisar manualmente los casos dudosos, es un **padrón candidato depurado de 254 establecimientos posibles**. Ese universo combina tres planos distintos: el registro administrativo oficial (AGC / F02), un relevamiento abierto auxiliar (OpenStreetMap) y una señal operativa no oficial (Google Places).

Principales hallazgos:

- **Predominan las casas independientes y de escala barrial**: 173 de los 254 candidatos, frente a 81 vinculados a cadenas.
- **El rubro se concentra** en las comunas 13, 14, 12, 5 y 6, y en los barrios de Palermo, Caballito, Belgrano, Recoleta y Villa Urquiza.
- **La lectura por densidad reordena el mapa**: al medir candidatos por km², sobresalen barrios como Almagro, Colegiales y Villa Urquiza, que no encabezan el ranking por cantidad absoluta.
- **53 candidatos cuentan con respaldo en más de una fuente** (Google + OSM): son el núcleo de mayor solidez del universo.
- **El registro oficial estricto es acotado** (11 candidatos por AGC / F02): mide habilitaciones, no locales activos, y por sí solo no alcanza para dimensionar el rubro.

Qué permite observar: el tamaño aproximado del rubro por comuna y barrio, dónde se forman polos, la relación entre cadenas y casas independientes, y qué parte del universo tiene mayor respaldo.

Qué oportunidades abre: aplicar el mismo método replicable a otros rubros gastronómicos y priorizar dónde vale la pena una validación territorial.

Límites del análisis: sigue siendo un padrón candidato; no confirma locales activos; incorpora fuentes no oficiales (Google / OSM); y la revisión de escritorio, aunque depura, no reemplaza la verificación en territorio si el informe se usa públicamente.

---

## 2. Objetivo y alcance

**Objetivo.** Aproximar el universo operativo probable de casas de pastas en la Ciudad de Buenos Aires y describir su distribución territorial, con trazabilidad de fuentes y de la revisión manual, para orientar validaciones y decisiones de gestión.

**Universo analizado.** Casas y fábricas de pastas en CABA, entendidas como establecimientos de elaboración y/o venta de pastas frescas o secas. Quedan expresamente fuera del rubro los restaurantes italianos, trattorias, pasta bars, pizzerías y gastronómicos generales.

**Fuentes utilizadas.**

- Registro administrativo oficial: AGC / F02 (habilitaciones).
- Relevamiento abierto auxiliar: OpenStreetMap.
- Señal operativa no oficial: Google Places (API oficial, sin scraping).
- Geometrías oficiales GCBA (comunas y barrios) para la asignación territorial.

**Qué queda fuera del alcance.**

- No es un censo ni un padrón oficial, ni reemplaza el registro administrativo.
- No afirma que un candidato sea un "local activo": el registro oficial mide habilitaciones.
- No incorpora fuentes de plataformas privadas por scraping.
- No calcula densidad por habitante (falta el denominador poblacional local); la densidad se expresa por superficie.

---

## 3. Metodología y fuentes

El universo se construyó cruzando cuatro planos de información y depurándolos con revisión manual. La metodología ampliada (criterios de clasificación, deduplicación, geocodificación y gobernanza de datos) se detalla en el **Anexo A**; aquí se concentra lo esencial para leer el informe.

**Los cuatro planos de fuente y qué puede afirmar cada uno.**

| Fuente | Naturaleza | Candidatos | Qué puede / no puede afirmar |
|---|---|---|---|
| AGC / F02 | Registro administrativo **oficial** | 11 | Habilitaciones; **no implica local activo** |
| OpenStreetMap | **Abierta auxiliar** | 145 | Cobertura territorial; **no oficial** |
| Google Places | **Operativa no oficial** | 150 | Visibilidad comercial; **no gubernamental** |
| Padrón depurado | **Padrón candidato** | 254 | Unión deduplicada + revisión manual |

_Los conteos corresponden al padrón integrado ya consolidado; no representan resultados brutos de búsqueda._

**Por qué el registro oficial no alcanza por sí solo.** El registro administrativo estricto (AGC / F02) aporta 11 candidatos: mide habilitaciones vinculadas a la elaboración de pastas, no locales activos, y el rubro registral es angosto (subrepresenta casas de pastas inscriptas bajo rubros genéricos). Por eso se complementa con fuentes abiertas y una señal operativa, sin mezclar universos: cada candidato conserva de qué fuente proviene.

**Cómo se consolidó el universo.** Los registros que refieren al mismo establecimiento se agrupan (deduplicación conservadora por nombre, dirección y proximidad geográfica) y se asignan a comuna y barrio por punto-en-polígono contra las geometrías oficiales GCBA. Cada candidato conserva trazabilidad de las fuentes que lo detectan y de su clasificación.

**Qué es y qué no es este padrón.** Es una unión deduplicada de fuentes, revisada manualmente en los casos dudosos. No es un padrón oficial ni un censo definitivo: es una base analítica para validación territorial.

---

## 4. Caracterización general del universo

El padrón candidato depurado queda conformado por **254 establecimientos posibles**.

- **254** candidatos únicos.
- **173** independientes / de barrio · **81** en cadenas.
- **53** con respaldo en más de una fuente (multifuente).
- **252** georreferenciados.

_252 de los 254 candidatos cuentan con coordenadas suficientes para su ubicación puntual; los 2 restantes integran el conteo general pero no se grafican._

**Composición por origen de fuente.**

| Combinación de fuentes | Candidatos |
|---|---|
| Solo OSM | 92 |
| Solo Google | 90 |
| Google + OSM | 53 |
| Solo AGC | 11 |
| Recall complementario (cobertura) | 7 |
| Documental (revisión) | 1 |
| **Total** | **254** |

---

## 5. Principales resultados

### 5.1. Concentración territorial (cantidad)

**Dato.** Las comunas con más candidatos son la 13 (33), 14 (30), 12 (24), 5 (23) y 6 (23). Por barrio, encabezan Palermo (30), Caballito (23), Belgrano (22), Recoleta (21) y Villa Urquiza (19).

**Lectura.** El rubro se concentra en el corredor norte y en el eje central-oeste de la Ciudad, con Palermo y Caballito como referencias claras.

**Implicancia.** Estas comunas y barrios son los candidatos naturales para una primera validación territorial, por volumen de establecimientos a verificar.

### 5.2. Densidad por km²

**Dato.** Por densidad de candidatos por km², las comunas líderes son la 5 (3.45), 6 (3.36), 2 (3.26), 13 (2.22) y 14 (1.88). Por barrio: Almagro (4.20), Colegiales (3.49), Villa Urquiza (3.49), Caballito (3.36) y Recoleta (3.26).

**Lectura.** El ranking por densidad **difiere** del de cantidad absoluta: barrios más chicos y compactos, como Almagro o Colegiales, muestran una concentración relativa alta que la lectura por cantidad no revela. No es densidad por habitante.

**Implicancia.** Cantidad y densidad responden preguntas distintas: dónde hay más establecimientos frente a dónde están más concentrados por superficie. Conviene leerlas juntas para no sobreponderar barrios grandes.

### 5.3. Polos del rubro

**Dato.** Palermo (30), Caballito (23) y Belgrano (22) encabezan el ranking por cantidad. Existen mapas de zoom para Palermo, Caballito y Belgrano.

**Lectura.** Estos tres barrios funcionan como polos del rubro por acumulación de establecimientos.

**Implicancia.** Son la base más evidente para trabajo territorial focalizado y para comunicar dónde se concentra la oferta.

### 5.4. Cadenas frente a casas independientes

**Dato.** En el universo candidato predominan las casas independientes y de escala barrial: **173 de 254**, frente a **81** vinculados a cadenas. Las principales cadenas por sucursales son LA JUVENIL (28), MULTIPASTA (7), CAPRIZZI (4), y con 2 sedes cada una MASTER PASTAS / PASTAS MASTER, MILENA PASTAS ARTESANALES, PASTAS MAZZEO y RAVIOLON, entre otras (detalle completo en el Anexo D).

**Lectura.** El rubro tiene una fuerte impronta independiente y barrial; las cadenas existen pero no dominan el universo. El listado de cadenas funciona además como control de cobertura (evita contar una misma marca como muchos establecimientos distintos).

**Implicancia.** La política hacia el rubro convive con un tejido mayoritariamente independiente, lo que es relevante para cualquier estrategia de acompañamiento o difusión.

### 5.5. Núcleo de mayor respaldo cruzado

**Dato.** 53 candidatos aparecen en más de una fuente (Google + OSM): es la base más sólida del universo. Las combinaciones son: solo OSM 92 · solo Google 90 · Google + OSM 53 · solo AGC 11 · recall complementario 7 · documental 1.

**Lectura.** Aparecer en más de una fuente aumenta la probabilidad de existencia, pero **no la confirma**: no reemplaza la validación.

**Implicancia.** Si se prioriza una validación por muestreo, este núcleo multifuente es el punto de partida de mayor confianza.

### 5.6. Aporte de la revisión manual

**Dato.** La revisión manual permitió depurar los casos dudosos detectados por el cruce de fuentes: se confirmaron 27 candidatos y se excluyeron 15 casos (restaurantes, locales cerrados, registros genéricos o rubros no incluidos). Una búsqueda complementaria de cobertura detectó 7 candidatos adicionales, incorporados solo tras revisión y trazabilidad.

**Lectura.** El cruce automático de fuentes deja casos ambiguos que sólo se resuelven con revisión de escritorio; esa capa mejora la calidad del padrón sin inflarlo.

**Implicancia.** El padrón depurado es más confiable que el cruce bruto, pero la revisión de escritorio no equivale a verificación en territorio. El detalle por caso queda en el anexo metodológico interno.

---

## 6. Lectura territorial

La distribución del rubro admite dos lecturas complementarias:

- **Por cantidad**, el rubro se concentra en el corredor norte (comunas 13 y 14; Palermo, Belgrano, Recoleta) y el eje central-oeste (comunas 12, 5 y 6; Caballito, Villa Urquiza).
- **Por densidad por km²**, sobresalen barrios más compactos (Almagro, Colegiales, Villa Urquiza), donde la concentración relativa es alta aunque el volumen absoluto sea menor.

Ambas lecturas describen el mismo universo desde ángulos distintos. La cantidad orienta el esfuerzo de validación por volumen; la densidad señala dónde la oferta está territorialmente más apretada. Las tablas completas por comuna y barrio (cantidad y densidad) están en el **Anexo B**.

Nota metodológica: la densidad se expresa por superficie (área oficial GCBA), no por población. En barrios con pocos candidatos, los valores de densidad son sensibles al tamaño del área y deben leerse con prudencia.

---

## 7. Lectura institucional

Qué confirma. El rubro tiene presencia significativa y distribuida en la Ciudad, con un perfil mayoritariamente independiente y barrial y polos claros en Palermo, Caballito y Belgrano. También confirma que el registro administrativo estricto, por sí solo, no alcanza para dimensionar el rubro.

Qué oportunidad abre. El método aplicado (registro oficial + fuentes abiertas + señal operativa + revisión manual) **podría** replicarse en otros rubros gastronómicos —pizzerías, heladerías artesanales, cafeterías de especialidad, panaderías, parrillas, casas de empanadas— para construir bases analíticas comparables con esfuerzo acotado.

Qué convendría observar. **Convendría** priorizar una validación territorial sobre el núcleo multifuente y sobre los polos de mayor concentración, donde el retorno de la verificación sería mayor.

Qué podría mejorarse. **Sería conveniente evaluar** la incorporación de población local para calcular densidad por habitante, y una actualización periódica de las fuentes, de modo de acercar el padrón candidato a una foto más cercana a la operación real.

El lenguaje de esta sección es deliberadamente prudente: se trata de lecturas y oportunidades, no de acciones decididas.

---

## 8. Aspectos a considerar

Lista priorizada, sin repetir el detalle del cuerpo:

1. **Habilitaciones no son locales activos.** El registro oficial mide habilitaciones; un registro puede estar cerrado hoy.
2. **Es un padrón candidato, no un censo.** No reemplaza al registro oficial ni la verificación en territorio.
3. **Fuentes no oficiales incluidas.** Google y OSM aportan cobertura, pero no son fuentes gubernamentales ni están verificadas.
4. **Rubro registral angosto.** El universo AGC estricto subrepresenta casas de pastas inscriptas bajo rubros genéricos.
5. **Densidad por superficie, no por habitante.** Con N pequeño en algunas áreas, los rankings de densidad son sensibles.
6. **Revisión de escritorio, no de campo.** Depura, pero no confirma existencia ni actividad en el lugar.

---

## 9. Próximos pasos

Si se decide avanzar, las líneas posibles son:

- **Validación territorial** del núcleo multifuente y de los polos de mayor concentración (muestreo priorizado).
- **Mejora de fuentes**: incorporación de población local para densidad por habitante; actualización periódica de AGC / OSM / Google.
- **Actualización de datos** del padrón candidato con nueva evidencia y trazabilidad.
- **Futuras visualizaciones**: mapas por barrio y comuna, y comparación cantidad vs densidad.
- **Cruces posibles**: replicar el método en otros rubros gastronómicos para bases comparables.

Estas líneas son opciones de trabajo, no compromisos de ejecución.

---

## 10. Anexos

### Anexo A — Metodología ampliada

**Clasificación de candidatos (criterio estricto A / B / C).**

- **A (estricto):** términos concluyentes de casa de pastas (elaboración/fábrica de pastas, casa de pastas, pastificio, venta de pastas frescas, y productos como ravioles, sorrentinos, ñoquis, fideos/tallarines frescos).
- **B (probable):** mención de pastas con contexto de producción/venta sin rubro concluyente; va a revisión manual y **no desaparece**.
- **C (dudoso/descartado):** mención de pasta junto a señales de restaurante/italiano/pizzería/bar/trattoria, o sin señal real de pasta. Se conservan aparte para trazabilidad.

Exclusiones que empujan a C (salvo match estricto): restaurant, trattoria, ristorante, pizza, parrilla, bar, cervecería, café, heladería, panadería, confitería, cocina italiana, pasta bar, comida italiana, resto.

**Tratamiento de Google en capas.** Google A (probable) entra como candidato fuerte; Google B no se descarta y va a revisión manual; Google C con señal de "posible faltante" va a revisión manual (no se promueve automáticamente); Google C descartado (restaurantes, trattorias, pasta bars, pizzerías, bares) se mantiene descartado y preservado.

**Deduplicación entre fuentes.** Se agrupan registros del mismo establecimiento combinando `place_id` (solo Google), nombre normalizado, dirección normalizada, distancia geográfica (haversine) y similitud de nombre. Reglas conservadoras (para no unir independientes distintos): dist<40 m y similitud ≥0.5; ó dist<150 m y similitud ≥0.8; ó nombre idéntico y dist<250 m. Cada registro conserva las fuentes que lo detectan, cantidad de fuentes, fuente principal, confianza integrada y si requiere revisión manual.

**Asignación territorial.** Punto-en-polígono contra las geometrías oficiales GCBA (comunas y barrios). Para AGC se respeta la comuna/barrio del maestro; para Google/OSM se asigna por coordenadas. Áreas en km² tomadas de las propiedades oficiales de las geometrías.

**Clasificación integrada (clases del padrón).**

| Clase | Regla |
|---|---|
| `A_integrado_multifuente` | Evidencia A en ≥2 fuentes (mayor confianza). |
| `A_agc_oficial_estricto` | Solo AGC. Oficial, pero **no implica local activo**. |
| `A_google_probable` | Solo Google A. Candidato operativo no oficial. |
| `A_osm_auxiliar` | Solo OSM A. Auxiliar. |
| `B_revision_manual` | Google B, OSM B o C "posible faltante". No desaparecen. |
| `C_descartado` | Restaurantes/bares/etc. Se conservan aparte. |

Aparecer en más de una fuente **sube** la confianza. Las casas independientes **no** bajan de prioridad por ser de una sola fuente: son centrales.

**Cadenas vs independientes.** Se marca cadena si el nombre coincide con una marca conocida o si el nombre normalizado aparece en ≥2 sedes; si aparece una sola vez y no es marca conocida, independiente.

**Reglas respetadas.** No se usó Google Drive ni fuentes internas. No se hizo scraping de plataformas privadas. No se llamaron APIs pagas fuera de la señal operativa oficial acotada; OSM (abierto) solo bajo ejecución explícita. No se llamó "locales activos" a las habilitaciones AGC. No se presentó OSM como padrón oficial. No se tocó el pipeline principal ni sus salidas. Universos A y B siempre separados.

### Anexo B — Tablas completas por comuna y barrio

**Comunas — cantidad y densidad (candidatos por km²).**

| Comuna | Candidatos | Área km² | Densidad (cand./km²) |
|---|---|---|---|
| 13 | 33 | 14.85 | 2.22 |
| 14 | 30 | 15.92 | 1.88 |
| 12 | 24 | 15.57 | 1.54 |
| 5 | 23 | 6.66 | 3.45 |
| 6 | 23 | 6.85 | 3.36 |
| 2 | 21 | 6.43 | 3.26 |
| 7 | 19 | 12.42 | 1.53 |
| 11 | 19 | 14.12 | 1.35 |
| 10 | 14 | 12.66 | 1.11 |
| 1 | 12 | 17.80 | 0.67 |
| 15 | 12 | 14.32 | 0.84 |
| 4 | 8 | 21.69 | 0.37 |
| 9 | 8 | 16.51 | 0.48 |
| 3 | 6 | 6.39 | 0.94 |
| 8 | 2 | 22.23 | 0.09 |

**Barrios — cantidad y densidad (candidatos por km²).** Ordenados por cantidad.

| Barrio | Comuna | Candidatos | Área km² | Densidad (cand./km²) |
|---|---|---|---|---|
| Palermo | 14 | 30 | 15.92 | 1.88 |
| Caballito | 6 | 23 | 6.85 | 3.36 |
| Belgrano | 13 | 22 | 8.06 | 2.73 |
| Recoleta | 2 | 21 | 6.43 | 3.26 |
| Villa Urquiza | 12 | 19 | 5.45 | 3.49 |
| Almagro | 5 | 17 | 4.05 | 4.20 |
| Flores | 7 | 15 | 8.59 | 1.75 |
| Villa Devoto | 11 | 10 | 6.40 | 1.56 |
| Colegiales | 13 | 8 | 2.29 | 3.49 |
| Villa Crespo | 15 | 7 | 3.62 | 1.94 |
| Monserrat | 1 | 5 | 2.20 | 2.27 |
| Villa del Parque | 11 | 5 | 3.40 | 1.47 |
| Boedo | 5 | 5 | 2.61 | 1.92 |
| Balvanera | 3 | 4 | 4.34 | 0.92 |
| San Nicolás | 1 | 4 | 2.29 | 1.75 |
| Villa Real | 10 | 4 | 1.33 | 3.00 |
| Parque Chacabuco | 7 | 4 | 3.83 | 1.04 |
| Saavedra | 12 | 4 | 5.54 | 0.72 |
| Liniers | 9 | 4 | 4.37 | 0.91 |
| Parque Patricios | 4 | 3 | 3.74 | 0.80 |
| Barracas | 4 | 3 | 7.96 | 0.38 |
| Villa Santa Rita | 11 | 3 | 2.15 | 1.39 |
| Mataderos | 9 | 3 | 7.40 | 0.41 |
| Villa Luro | 10 | 3 | 2.57 | 1.17 |
| Parque Chas | 15 | 2 | 1.39 | 1.44 |
| Floresta | 10 | 2 | 2.32 | 0.86 |
| Vélez Sarsfield | 10 | 2 | 2.40 | 0.83 |
| Núñez | 13 | 2 | 4.50 | 0.44 |
| La Boca | 4 | 2 | 5.04 | 0.40 |
| Monte Castro | 10 | 2 | 2.63 | 0.76 |
| San Telmo | 1 | 2 | 1.23 | 1.62 |
| San Cristóbal | 3 | 2 | 2.04 | 0.98 |
| Agronomía | 15 | 1 | 2.12 | 0.47 |
| Retiro | 1 | 1 | 4.51 | 0.22 |
| Versalles | 10 | 1 | 1.41 | 0.71 |
| Parque Avellaneda | 9 | 1 | 4.73 | 0.21 |
| Coghlan | 12 | 1 | 1.28 | 0.78 |
| Villa Ortúzar | 15 | 1 | 1.85 | 0.54 |
| Chacarita | 15 | 1 | 3.12 | 0.32 |
| Villa Gral. Mitre | 11 | 1 | 2.16 | 0.46 |
| Villa Soldati | 8 | 1 | 8.69 | 0.12 |
| Villa Lugano | 8 | 1 | 9.30 | 0.11 |

_La comuna asignada a cada barrio proviene de la geometría oficial GCBA; la densidad se expresa por superficie, no por habitante._

### Anexo C — Casos con respaldo documental

Además del análisis territorial, se identificaron establecimientos con fuentes sobre trayectoria, origen familiar o antigüedad. No es un ranking histórico exhaustivo, sino ejemplos verificables dentro del rubro.

- **Pastas Amelia** — Boedo · 1948 — fábrica artesanal vinculada a la familia Palazzo (fusilis al fierrito).
- **La Hispano Americana** — San Telmo · más de medio siglo — casa de pastas asociada a inmigrantes gallegos y continuidad familiar.
- **La Juvenil** — Colegiales · 1959 — marca familiar con varias generaciones y expansión territorial.
- **Pastas Bayo** — Belgrano · 1978 — casa de pastas familiar con permanencia en la misma dirección.

_Se incluyen por contar con fuentes documentales identificables (prensa nacional y sitios oficiales); no agotan la historia del rubro ni prueban por sí solos cuál es la casa de pastas más antigua de la Ciudad. Detalle de fuentes en anexo metodológico interno._

### Anexo D — Detalle de cadenas

Principales cadenas por cantidad de sucursales detectadas (control de cobertura):

- LA JUVENIL (28)
- MULTIPASTA (7)
- CAPRIZZI (4)
- MASTER PASTAS / PASTAS MASTER (2), MILENA PASTAS ARTESANALES (2), PASTAS MAZZEO (2), RAVIOLON (2).

Otras marcas con 2 sedes detectadas en el universo integrado: BIASATTI, PASTAS BAYO, RICAPASTA, RAVIOLANDIA, LA LUISITA, LA GENOVESA, PIATTO ROSSO, SAN JOSE, STELLA MARIS, FARFALLA, LA CONFIANZA, ROCHINO, L'ARTISAN, entre otras.

El listado de cadenas cumple una doble función: describir el peso de las marcas en el rubro y evitar que una misma marca se cuente como muchos establecimientos independientes.

### Anexo E — Limitaciones metodológicas

- Sigue siendo un **padrón candidato**; no reemplaza al registro oficial ni implica local activo confirmado por fuente oficial.
- **Google y OSM no son fuentes oficiales.** Pueden existir locales cerrados o faltantes.
- La **densidad se expresa por superficie**; una etapa posterior puede incorporar población para estimar cobertura relativa por habitante.
- La **revisión manual de escritorio** mejora la depuración, pero no reemplaza la verificación territorial final si el informe se usa públicamente.

| ID | Limitación | Implicancia |
|---|---|---|
| L1 | AGC mide habilitaciones, no locales activos | Un registro puede estar cerrado hoy |
| L2 | Rubro AGC estricto angosto | Subrepresenta casas de pastas registradas bajo rubros genéricos |
| L3 | Geocodificación solo con caché local | Casos sin punto; sin servicios externos pagos |
| L4 | Sin población local | No se calcula densidad por habitante |
| L5 | OSM colaborativo e incompleto | No es padrón oficial; útil como contraste y para validar |
| L6 | N pequeño en algunas áreas | Rankings de densidad sensibles; diagnóstico inicial, no censo |
| L7 | Diferencia AGC vs OSM | No es error: es diferencia de fuente y definición |
