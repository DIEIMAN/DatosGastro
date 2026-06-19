# DataGastro — Documento de referencia para presentación

> Este documento es para que puedas leerlo antes de la presentación, entender el proyecto de punta a punta y explicarlo con confianza. Está escrito en lenguaje llano, sin código.

---

## 1. Qué es DataGastro y por qué existe

La Ciudad de Buenos Aires tiene un sector gastronómico muy activo: miles de restaurantes, bares, cafés, ferias de comida, mercados, festivales. Pero la información sobre ese sector estaba dispersa en varios registros oficiales que nunca nadie había integrado. Había una guía de oferta gastronómica publicada por Turismo, un registro de habilitaciones formales en la Agencia Gubernamental de Control, un padrón de ferias y mercados en otra dependencia, noticias sobre eventos en el portal de Cultura, y documentos sobre programas de gobierno en distintos ministerios. Cada uno describía una dimensión distinta del mismo ecosistema, pero nadie los había puesto juntos.

**DataGastro nació para resolver ese problema.** La idea central no fue producir "un número" que lo dijera todo, sino integrar esas fuentes en una base analítica ordenada, trazable y metodológicamente honesta. El producto final es una base de datos con pipeline de procesamiento, un dashboard interactivo para explorar los datos, y un informe de análisis completo que se puede reproducir cuando se actualicen los datos.

El valor principal no está en los números en sí —que son públicos y estaban disponibles— sino en haberlos ordenado, limpiado, corregido y convertido en algo que se puede usar para tomar decisiones.

---

## 2. Las cinco fuentes que integra DataGastro

### Fuente 1 — Oferta gastronómica registrada
**Organismo:** Ente de Turismo del Gobierno de la Ciudad de Buenos Aires  
**Qué es:** La guía oficial de gastronomía de la Ciudad. Un listado de 2.823 establecimientos con nombre, dirección, categoría (restaurante, bar, café, etc.) y datos de contacto.  
**Para qué sirve:** Saber dónde están y de qué tipo son los establecimientos que el Gobierno de la Ciudad reconoce oficialmente como oferta gastronómica.  
**Límite importante:** Esta guía es estática — no se actualiza cuando cierra un local. No confirma que cada establecimiento sigue operativo hoy.

### Fuente 2 — Habilitaciones gastronómicas aprobadas
**Organismo:** Agencia Gubernamental de Control (AGC) del Gobierno de la Ciudad de Buenos Aires  
**Qué es:** El registro de habilitaciones comerciales aprobadas por rubro, descargado del portal de datos abiertos por año (2015 a 2024). Son 44.169 habilitaciones gastronómicas.  
**Para qué sirve:** Ver la evolución formal del sector año a año. Una habilitación aprobada marca dónde el sector formal está invirtiendo, qué tipo de gastronomía se está habilitando, y en qué territorios.  
**Límite importante:** Una habilitación aprobada no es un local activo. La fuente registra autorizaciones pero no registra cuando un local cierra. No se puede calcular cuántos locales están abiertos hoy a partir de esta fuente.

### Fuente 3 — Ferias, mercados y Ferias Itinerantes de Abastecimiento Barrial
**Organismo:** Dirección General de Ferias del Ministerio de Ambiente y Espacio Público del GCBA  
**Qué es:** Los espacios públicos de abastecimiento que gestiona la Ciudad: 6 mercados municipales, 69 ferias especializadas y 184 puntos de Ferias Itinerantes de Abastecimiento Barrial (FIAB). Las FIAB son ferias de productos frescos y básicos (frutas, verduras, pescado, pan) que rotan por barrios según un cronograma oficial.  
**Para qué sirve:** Conocer la red de abastecimiento público de la Ciudad y su distribución territorial.  
**Límite importante:** Se cuenta el espacio (la feria, el mercado, el punto FIAB), no los puestos individuales ni las personas. Un mercado con 50 puestos sigue siendo 1 espacio, no 50.

### Fuente 4 — Eventos gastronómicos relevados
**Origen:** Relevamiento manual a partir de comunicaciones oficiales del GCBA (portal de noticias, Turismo, Cultura). Cada evento tiene la URL de la fuente anotada.  
**Qué es:** Un inventario de 13 eventos verificados: festivales gastronómicos, ciclos de mercado, concursos, jornadas de descuentos, participaciones institucionales.  
**Para qué sirve:** Mostrar que la Ciudad tiene una agenda gastronómica activa con eventos sostenidos en el tiempo.  
**Límite importante:** No es el universo completo de eventos de la Ciudad. Es lo que se pudo documentar y verificar con fuente oficial.

### Fuente 5 — Programas y políticas gastronómicas
**Origen:** Relevamiento manual de instituciones del GCBA, con normativa de referencia anotada.  
**Qué es:** Un catálogo de 4 programas vigentes verificados: BA Capital Gastronómica (programa marco de promoción sectorial), Distrito del Vino (incentivos fiscales en la Comuna 11), Programa de Bares Notables (protección de establecimientos patrimoniales), y el régimen de permisos de área gastronómica (mesas y sillas en vereda).  
**Para qué sirve:** Mostrar el marco institucional que rodea al sector.  
**Límite importante:** No mide impacto económico, empleo ni presupuesto ejecutado.

---

## 3. Cómo se construyó la base: el proceso paso a paso

El proceso de DataGastro tiene cuatro etapas principales que se pueden repetir cuando se actualicen los datos:

**Etapa 1 — Descarga de fuentes**  
Se descargaron automáticamente los archivos CSV de Buenos Aires Data (el portal de datos abiertos del GCBA) para Fuente 1, 2 y 3. Las fuentes 4 y 5 se construyeron manualmente con relevamiento y documentación de cada fila.

**Etapa 2 — Limpieza y normalización**  
Cada fuente tenía sus propios problemas:
- La guía de oferta (Fuente 1) tenía caracteres mal codificados que producían texto ilegible — se corrigió el encoding.
- Las habilitaciones (Fuente 2) tenían las direcciones en un formato invertido y con comas (tipo "FERNANDEZ DE LA CRUZ, F., GRAL. AV. 4602") — se desarrolló un normalizador específico.
- El padrón de ferias (Fuente 3) mezclaba puestos individuales con información personal de feriantes junto con los espacios reales — se separaron los niveles y se descartaron los datos personales.
- El clasificador de rubros gastronómicos de Fuente 2 se rediseñó para evitar falsos positivos (la versión original asignaba categorías gastronómicas a rubros como "talabartería" porque contenían palabras similares, inflando el total a más del doble del real).

**Etapa 3 — Geocodificación**  
Geocodificar significa convertir una dirección de texto en coordenadas geográficas para poder mostrarla en un mapa. Se usó el Sistema de Información Geográfica del GCBA (USIG), que es el normalizador oficial de la Ciudad. Se geocodificaron 42.741 habilitaciones (97% del total de Fuente 2), con una tasa de exactitud del 99%. La cache de geocodificación queda guardada para no repetir consultas ya procesadas.

**Etapa 4 — Validación**  
Antes de usar los datos en el dashboard o en los informes, el pipeline ejecuta 62 controles automáticos: integridad referencial entre tablas, consistencia de coordenadas dentro del territorio de la Ciudad, trazabilidad de fuentes, y reglas metodológicas (como que F01 y F02 no se suman). Los 62 controles pasaron sin errores ni advertencias.

---

## 4. Los hallazgos principales

### Hallazgo 1 — Los números del ecosistema (separados)

| Qué mide | Cantidad | Fuente |
|---|---|---|
| Oferta gastronómica registrada en guía oficial | 2.823 establecimientos | Fuente 1 — Ente de Turismo |
| Habilitaciones gastronómicas aprobadas (2015–2024) | 44.169 habilitaciones | Fuente 2 — AGC |
| De las cuales ubicadas en el mapa | 42.741 (97%) | Fuente 2 + USIG |
| Espacios de ferias, mercados y FIAB | 259 espacios reales | Fuente 3 — Dir. Gral. Ferias |
| Eventos verificados | 13 eventos | Fuente 4 — relevamiento |
| Programas vigentes verificados | 4 programas | Fuente 5 — relevamiento |

**El punto clave:** estos números no se suman. Cada uno describe una dimensión distinta del ecosistema.

### Hallazgo 2 — La distribución geográfica

La actividad gastronómica se concentra en el corredor norte (Palermo, Recoleta, Belgrano) y el centro histórico (San Nicolás, Monserrat, San Telmo), y se afina hacia el sur. Este patrón es consistente entre la guía de oferta (Fuente 1) y las habilitaciones geocodificadas (Fuente 2).

### Hallazgo 3 — El núcleo real es el microcentro, no Palermo

Este es el hallazgo más contraintuitivo y más útil para gestión. En números absolutos, Palermo tiene más establecimientos registrados que cualquier otro barrio. Pero Palermo es muy grande en superficie. Cuando se mide la **densidad** (cuántos registros hay por kilómetro cuadrado), el barrio de San Nicolás multiplica por seis o siete la concentración de Palermo.

Dicho de otro modo: **el corazón gastronómico por intensidad es el microcentro y el casco histórico, no Palermo**. Palermo tiene más locales en total, pero están más distribuidos en el espacio. El microcentro tiene menos locales pero muy comprimidos en poco territorio.

¿Por qué importa esta diferencia? Porque tiene implicancias distintas para política de uso del suelo, gestión del espacio público, permisos de mesas en vereda, flujo peatonal y saturación de servicios.

### Hallazgo 4 — La evolución formal del sector

La serie de habilitaciones 2019–2024 permite ver la dinámica anual: el impacto visible de la pandemia en 2020 (caída significativa de habilitaciones) y la recuperación posterior. Esta serie es útil para conversación con cualquier área de planificación porque muestra dinamismo formal del sector con datos oficiales y verificables.

### Hallazgo 5 — La Ciudad tiene una red de abastecimiento público relevante

Los 184 puntos de Ferias Itinerantes de Abastecimiento Barrial (FIAB) están distribuidos en todos los barrios de la Ciudad con lógica de proximidad — son ferias de productos básicos (frutas, verduras, pan, pescado) que rotan por esquinas según un cronograma. Sumados a los 6 mercados municipales y las 69 ferias especializadas, conforman una red pública de abastecimiento con mayor equilibrio territorial que la oferta privada.

---

## 5. Lo que NO dice la base (límites honestos)

Este es el punto más importante para anticipar preguntas difíciles en la presentación.

**DataGastro NO responde:**

- **Cuántos locales están activos hoy.** No existe una fuente con ese dato. La guía de oferta es estática, y las habilitaciones no registran cierres.

- **Cuántos locales abrieron o cerraron en términos netos.** Las habilitaciones son autorizaciones, no confirmaciones de apertura efectiva.

- **El impacto económico del sector:** empleo, facturación, ventas, contribución al producto bruto de la Ciudad.

- **Si un barrio está saturado o subatendido.** Para eso haría falta cruzar la oferta con la demanda (cuánta gente vive, trabaja o visita cada zona), y esos datos no están integrados todavía.

- **El impacto de los eventos o programas.** No hay métricas de resultado publicadas para la mayoría de los programas relevados.

Decir estas limitaciones de frente no es una debilidad del proyecto — es parte de su valor. Una base que sabe lo que sabe y lo que no sabe es mucho más útil que una que hace afirmaciones que los datos no sostienen.

---

## 6. La novedad metodológica: qué hace diferente a DataGastro

Hay tres cosas técnicas que merecen mención porque representan trabajo real y defienden la calidad del resultado:

**Separación estricta de universos**  
La regla central del proyecto es que las fuentes no se suman cuando miden cosas distintas. Esto parece obvio, pero en la práctica es muy fácil sumar habilitaciones con oferta registrada y decir "hay X establecimientos gastronómicos", lo que sería un número sin respaldo. DataGastro explícitamente no hace eso y documenta por qué.

**Geocodificación con el normalizador oficial del GCBA**  
Convertir 44.000 direcciones en coordenadas con el normalizador oficial de la Ciudad (USIG), con control de calidad por fila y cache persistente, es trabajo técnico que agrega una capa de información que no existía antes: la posibilidad de ver, calle por calle, dónde se aprueba actividad gastronómica formal en la Ciudad.

**Control de calidad automatizado**  
Los 62 controles automáticos del pipeline garantizan que cada vez que se actualicen los datos, el mismo nivel de calidad se mantiene. No es un proceso manual que depende de que alguien recuerde qué revisar.

---

## 7. Los próximos pasos

**Paso 1 — Incorporar permisos de área gastronómica (Fuente 6)**  
Los permisos de mesas y sillas en la vía pública son un trámite anual. Un local que renueva ese permiso probablemente sigue abierto. Esta fuente cubriría el mayor vacío actual: no tener información de actividad vigente.

**Paso 2 — Exportar el informe a PDF para circulación**  
El informe de análisis completo (notebook 07) se puede convertir en un documento HTML o PDF con un comando, listo para circular internamente.

**Paso 3 — Módulo de análisis de redes (exploratorio)**  
Aplicar herramientas de análisis de grafos sobre los puntos geocodificados para detectar polos gastronómicos, corredores y comunidades de barrios similares. Este paso es exploratorio y sus resultados no serían indicadores oficiales.

---

## 8. Los próximos pasos para la presentación

### Para explicar el proyecto en dos minutos

> "DataGastro integra cinco fuentes de datos oficiales del GCBA sobre gastronomía — oferta registrada, habilitaciones, ferias y mercados, eventos y programas — en una base analítica única y reproducible. Lo que hace diferente a esto de simplemente descargar un CSV es que cada fuente fue limpiada, corregida, geocodificada con el normalizador oficial de la Ciudad, y validada con 62 controles automáticos. El resultado es una base que permite hacer diagnósticos territoriales rápidos, ver la evolución formal del sector, y tener evidencia trazable detrás de cada número."

### Para responder la pregunta difícil sobre locales activos

> "Esa es exactamente la brecha que identificamos. Hoy no existe en los datos abiertos del GCBA un padrón con fecha de baja de establecimientos gastronómicos. Lo que sí tenemos es la guía de oferta registrada y las habilitaciones aprobadas, pero ninguna de las dos dice si un local está abierto hoy. El próximo paso concreto para resolver eso es incorporar los permisos de área gastronómica — las mesas y sillas en vereda — que se renuevan anualmente y son la señal de actividad vigente más directa que está disponible."

### Para explicar el hallazgo de densidad vs. volumen

> "El dato más interesante que encontramos es que Palermo no es el barrio más gastronómico de la Ciudad cuando se mide por intensidad. En números absolutos sí tiene más locales registrados, pero cuando se divide por la superficie del barrio, San Nicolás tiene seis o siete veces más concentración gastronómica por kilómetro cuadrado. El corazón real del sector por densidad es el microcentro y el casco histórico, no Palermo. Esa diferencia importa mucho a la hora de planificar uso del suelo o permisos de espacio público."

---

## 9. Glosario de términos y siglas

| Término | Qué significa |
|---|---|
| AGC | Agencia Gubernamental de Control — organismo del GCBA que aprueba habilitaciones comerciales |
| GCBA | Gobierno de la Ciudad de Buenos Aires |
| USIG | Sistema de Información Geográfica — servicio oficial del GCBA para normalizar y ubicar direcciones en el mapa |
| FIAB | Ferias Itinerantes de Abastecimiento Barrial — ferias de productos frescos que rotan por barrios según cronograma |
| Geocodificación | Convertir una dirección de texto en coordenadas geográficas (latitud y longitud) para mostrarla en el mapa |
| Habilitación | Autorización formal que otorga el GCBA para operar un rubro comercial en una dirección |
| Pipeline | El proceso automatizado que descarga, limpia, integra y valida los datos |
| F01 a F05 | Nombres internos de las cinco fuentes del proyecto (no los usamos en la presentación) |
| Dashboard | Panel interactivo en el navegador para explorar los datos con filtros |
| Densidad gastronómica | Cuántos establecimientos hay por kilómetro cuadrado — más útil que el volumen absoluto para comparar barrios de distinto tamaño |
| Trazabilidad | La capacidad de saber de dónde viene cada dato: qué fuente, qué fecha, qué URL |
| Padrón vivo | Un registro actualizado en tiempo real de qué locales están activos — DataGastro no tiene esto todavía |
| Serie comparable | El subconjunto de datos que se puede comparar en el tiempo sin distorsión (en este caso, habilitaciones 2019–2024) |

---

*DataGastro — primera base analítica del ecosistema gastronómico de la Ciudad de Buenos Aires.*  
*Datos abiertos del GCBA y relevamientos trazables. Cada número informa su fuente, su fecha y sus límites.*
