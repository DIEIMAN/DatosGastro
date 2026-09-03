# Propuesta metodologica: modulo Red gastronomica de CABA

## Estado de la propuesta

Este documento propone una linea futura de trabajo para DataGastro, posterior a la demo. No implica cambios en el pipeline actual, no modifica el dashboard y no incorpora dependencias nuevas.

La propuesta toma como inspiracion metodologica el trabajo practico de ALC sobre grafos, PageRank, matrices de adyacencia, laplacianos, modularidad y deteccion de comunidades. En DataGastro, esas herramientas podrian usarse como analisis exploratorio para estudiar relaciones territoriales y de perfil gastronomico dentro de CABA.

## 1. Objetivo del modulo

El modulo "Red gastronomica de CABA" tendria como objetivo representar el ecosistema gastronomico como una red de relaciones entre establecimientos registrados, habilitaciones aprobadas, territorios y categorias.

La pregunta general no seria "cuantos locales hay", sino como se conectan territorial y funcionalmente distintas zonas de la ciudad:

- que barrios aparecen como conectores entre zonas gastronomicas;
- que comunas comparten perfiles similares;
- que categorias gastronomicas estructuran concentraciones territoriales;
- donde aparecen subredes o comunidades con comportamiento parecido;
- que zonas ocupan posiciones centrales en la red gastronomica observada.

El modulo podria servir como laboratorio analitico para detectar patrones, formular hipotesis y orientar preguntas de gestion publica que luego deban validarse con fuentes adicionales.

## 2. Por que es exploratorio y no una metrica oficial

El analisis de redes no deberia presentarse como indicador oficial de actividad gastronomica. Seria una lectura derivada, sensible a decisiones metodologicas y a parametros de construccion del grafo.

En particular:

- F01 mide oferta registrada, pero no confirma vigencia operativa actual de cada registro.
- F02 mide habilitaciones aprobadas, no locales activos.
- F02 geocodificada con USIG mejora la lectura territorial, pero sigue representando habilitaciones, no establecimientos en funcionamiento.
- La definicion de aristas depende de umbrales de distancia, cantidad de vecinos, agregacion territorial o criterios de similitud.
- Cambios pequenos en parametros pueden alterar centralidades, comunidades y rankings.

Por eso, cualquier resultado deberia leerse como exploracion metodologica y no como una medicion administrativa consolidada.

## 3. Nodos posibles

El modulo podria ensayar distintos tipos de nodos, segun la pregunta de gestion.

### F01 establecimientos registrados

Podrian usarse como nodos puntuales cuando se quiera estudiar la oferta registrada con coordenadas de fuente oficial.

Uso recomendado:

- analizar proximidad entre registros;
- identificar zonas de alta conectividad en la oferta observada;
- explorar perfiles de categorias por territorio.

Advertencia:

- no interpretar F01 como padron completo de locales activos sin validacion adicional.

### F02 habilitaciones geocodificadas agrupadas

F02 podria incorporarse como nodos agregados, por ejemplo por barrio, comuna, celda espacial o combinacion territorio-categoria.

Uso recomendado:

- medir intensidad formal historica de habilitaciones;
- comparar patrones de habilitacion entre comunas o barrios;
- complementar la lectura de F01 sin fusionar universos.

Advertencia:

- no llamar locales activos a F02;
- no mezclar registros F01 y F02 como si fueran la misma unidad;
- mantener F02 como habilitaciones aprobadas, aun cuando tenga punto USIG validado.

### Barrios

Los barrios podrian ser nodos de una red territorial. Cada barrio tendria atributos derivados de F01, F02 y categorias, siempre separados por fuente.

Uso recomendado:

- comparar perfiles gastronomicos;
- detectar similitudes entre barrios no necesariamente contiguos;
- estudiar centralidad territorial dentro de la red urbana.

### Comunas

Las comunas podrian funcionar como nodos de mayor agregacion, utiles para gestion publica y comunicacion institucional.

Uso recomendado:

- observar patrones macroterritoriales;
- comparar intensidad relativa por comuna;
- construir redes simples de adyacencia territorial o similitud de perfil.

### Categorias gastronomicas

Las categorias podrian ser nodos cuando la pregunta se centre en el perfil de actividad y no en el territorio.

Uso recomendado:

- analizar coocurrencias categoria-territorio;
- detectar categorias que conectan barrios o comunas;
- observar diversidad o especializacion gastronomica.

## 4. Aristas posibles

Las aristas definirian que significa que dos nodos estan relacionados. Esta decision es central y deberia documentarse en cada notebook.

### Proximidad espacial

Dos nodos puntuales podrian conectarse si estan dentro de un radio determinado o si uno esta entre los vecinos mas cercanos del otro.

Ejemplos:

- conectar cada establecimiento F01 con sus `k` vecinos mas cercanos;
- conectar habilitaciones F02 agrupadas por celdas vecinas;
- construir redes por distancia maxima, por ejemplo 300, 500 o 800 metros.

### Distancia inversa

En lugar de una arista binaria, se podria asignar un peso proporcional a la cercania:

- mayor peso para puntos cercanos;
- menor peso para puntos lejanos;
- peso nulo para distancias fuera de un umbral.

Esta alternativa permite una red ponderada, pero aumenta la sensibilidad a parametros y requiere explicar la escala usada.

### Adyacencia territorial

Para barrios o comunas, las aristas podrian representar vecindad geografica.

Ejemplos:

- dos barrios conectados si comparten borde;
- dos comunas conectadas si son contiguas;
- aristas ponderadas por longitud de frontera compartida o por intensidad de flujos observados, si existieran datos confiables.

### Similitud de perfil gastronomico

Dos territorios podrian conectarse si tienen una composicion gastronomica parecida.

Ejemplos:

- similitud entre vectores de categorias F01 por barrio;
- similitud entre perfiles de habilitaciones F02 por comuna;
- similitud entre participaciones relativas de rubros, evitando comparar solo volumen absoluto.

Esta arista serviria para encontrar barrios parecidos aunque no sean vecinos.

## 5. Metricas exploratorias posibles

### PageRank

PageRank podria explorar que nodos quedan mejor conectados dentro de una red construida por proximidad o similitud.

Interpretacion posible:

- territorios con alta conectividad relativa;
- categorias que aparecen como puentes entre perfiles;
- nodos que concentran relacion estructural dentro del grafo.

No deberia interpretarse como "importancia economica" ni como ranking oficial de relevancia gastronomica.

### Centralidad

Se podrian explorar medidas de centralidad de grado, cercania o intermediacion.

Preguntas posibles:

- que barrios conectan subzonas gastronomicas;
- que comunas quedan cerca de muchas otras segun perfil;
- que categorias aparecen como articuladoras de distintos territorios.

### Diversidad gastronomica

La diversidad podria calcularse como atributo de nodos territoriales, no necesariamente como metrica de red pura.

Ejemplos:

- cantidad de categorias presentes;
- distribucion relativa entre categorias;
- indices simples de concentracion o diversidad.

Debe evitarse interpretar diversidad como calidad, oportunidad o impacto sin evidencia adicional.

### Modularidad

La modularidad permitiria evaluar si una particion en comunidades describe grupos de nodos mas conectados internamente que con el resto de la red.

Uso posible:

- detectar grupos de barrios con perfiles gastronomicos similares;
- observar comunidades territoriales en redes de proximidad;
- comparar particiones por distancia contra particiones por similitud de perfil.

### Clustering espectral

El clustering espectral podria aplicarse sobre la matriz de adyacencia o laplaciana para detectar grupos latentes.

Uso posible:

- segmentar barrios segun estructura de red;
- comparar cortes por laplaciano con comunidades por modularidad;
- explorar estabilidad de comunidades ante distintos parametros.

La salida deberia presentarse como agrupamiento exploratorio, no como clasificacion oficial de barrios.

### Similitud entre barrios

La similitud entre barrios podria convertirse en una matriz barrio-barrio basada en categorias, habilitaciones o combinaciones controladas de fuentes.

Uso posible:

- encontrar barrios con perfiles gastronomicos parecidos;
- detectar territorios comparables para politicas o relevamientos;
- construir mapas de afinidad que complementen la lectura por comuna.

## 6. Preguntas de gestion que podria responder

Si la notebook futura funciona y los supuestos quedan documentados, el modulo podria ayudar a responder preguntas como:

- Que barrios tienen perfiles gastronomicos similares aunque no sean contiguos?
- Que zonas aparecen como conectores entre concentraciones gastronomicas?
- Que comunas muestran mayor diversidad de categorias registradas?
- Que categorias estructuran comunidades territoriales?
- Como cambia la red si se usa proximidad espacial frente a similitud de perfil?
- Que territorios convendria analizar juntos para una politica de promocion, fiscalizacion o relevamiento?
- Donde puede haber patrones que merezcan trabajo cualitativo o validacion con nuevas fuentes?

Estas preguntas deben leerse como apoyo a la exploracion y priorizacion, no como decisiones automaticas.

## 7. Riesgos metodologicos

### No confundir densidad con oportunidad

Una zona con alta densidad de registros o habilitaciones no necesariamente representa oportunidad de intervencion. Puede indicar consolidacion, saturacion, mejor registro administrativo, mayor fiscalizacion o simplemente mayor disponibilidad de datos.

### No llamar locales activos a F02

F02 son habilitaciones aprobadas. Incluso con geocodificacion USIG, no deben presentarse como locales activos ni como establecimientos actualmente abiertos.

### No mezclar F01 y F02

F01 y F02 pueden compararse o ponerse en dialogo, pero no sumarse como un unico universo. Si se construyen redes combinadas, cada fuente debe mantener su semantica.

Ejemplo aceptable:

- red de barrios con atributos separados F01 y F02.

Ejemplo no aceptable:

- ranking de "establecimientos" que suma F01 y F02.

### Sensibilidad a parametros

Los resultados pueden cambiar por:

- radio de proximidad;
- cantidad de vecinos `k`;
- formula de peso por distancia;
- normalizacion de categorias;
- escala territorial usada;
- inclusion o exclusion de categorias ambiguas.

Toda salida deberia incluir parametros y pruebas de sensibilidad.

### No inferir causalidad

Una comunidad detectada en un grafo no explica por si misma por que ocurre un patron. Tampoco prueba impacto de una politica, evento o programa. Solo sugiere relaciones que pueden investigarse.

## 8. Notebook futura propuesta

La extension deberia desarrollarse primero como notebook exploratoria:

```text
notebooks/06_red_gastronomica_caba.ipynb
```

Objetivo de la notebook:

1. Cargar datos procesados ya existentes, sin modificar el pipeline.
2. Seleccionar una unidad de analisis: punto F01, agregado F02, barrio, comuna o categoria.
3. Construir una o mas matrices de adyacencia.
4. Documentar parametros: distancia, `k`, normalizacion, pesos y filtros.
5. Calcular metricas exploratorias.
6. Comparar resultados ante distintos parametros.
7. Generar tablas y visualizaciones candidatas.
8. Cerrar con una evaluacion metodologica: que parece robusto, que es sensible y que no debe publicarse.

La notebook no deberia escribir archivos en `data/processed` ni cambiar salidas actuales. Si mas adelante se decide producir derivados, deberian guardarse como artefactos exploratorios separados y claramente rotulados.

## 9. Resultados que podrian pasar al dashboard

Solo si la notebook muestra resultados estables y metodologicamente defendibles, algunos productos podrian pasar al dashboard como seccion exploratoria.

Posibles salidas:

- mapa de comunidades de barrios, con parametros visibles;
- tabla de barrios similares por perfil gastronomico;
- lectura de diversidad gastronomica por barrio o comuna;
- red simplificada de comunas por similitud de perfil;
- comparacion entre comunidades por proximidad y comunidades por perfil;
- advertencia metodologica fija que indique que no es indicador oficial.

Condiciones para pasar al dashboard:

- mantener F01, F02, barrios, comunas y categorias con semantica separada;
- mostrar fuente, fecha, filtros y parametros;
- evitar rankings normativos sin contexto;
- ubicarlo como modulo exploratorio posterior a la demo;
- conservar el dashboard principal sin depender de este modulo.

## 10. Que NO deberia mostrarse como indicador oficial

No deberian mostrarse como indicadores oficiales:

- PageRank de barrios como ranking de importancia gastronomica;
- comunidades como zonas oficiales de politica publica;
- centralidad como indicador de oportunidad economica;
- diversidad como indicador de exito o calidad;
- similitud entre barrios como equivalencia administrativa;
- densidad de habilitaciones F02 como cantidad de locales activos;
- combinaciones F01 + F02 como total de establecimientos;
- clusters espectrales sin parametros, sensibilidad y explicacion metodologica.

La regla de publicacion deberia ser: si una metrica depende fuertemente de parametros o mezcla interpretaciones de fuente, queda en notebook exploratoria y no pasa al tablero ejecutivo.

## Cierre

La Red gastronomica de CABA puede ser una extension potente para DataGastro, especialmente para explorar estructura territorial, perfiles de barrios y comunidades gastronomicas. Pero debe llegar despues de la demo, como linea de investigacion controlada, con metodologia explicita y sin reemplazar los indicadores descriptivos ya validados.

Su valor no estaria en producir un ranking definitivo, sino en abrir preguntas mejores para la gestion publica.
