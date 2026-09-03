# Informe de validación metodológica — Prototipo V1 de microzonas

**Fecha:** 2026-07-08 · **Carácter:** experimental. Síntesis de las Etapas V2-1 a V2-5
(casos de estudio, tableros visuales, diagnóstico editorial, segunda pasada, tipología).
No es un informe técnico de rendimiento del algoritmo: es una lectura metodológica de si
el resultado es creíble para alguien que conoce la gastronomía porteña.

## La pregunta que había que responder

> *Si una persona que conoce perfectamente la gastronomía de Buenos Aires mirara estos
> mapas, ¿diría que los microclusters representan correctamente la realidad?*

**Respuesta: sí, salvo algunos casos puntuales — y esos casos puntuales tienen una causa
identificada, no son ruido aleatorio.** En 6 de los 8 casos de estudio (Palermo, Chacarita,
Villa Crespo, Belgrano, Microcentro/vía segunda pasada, y el núcleo central de San Telmo)
los clusters coinciden con lo que un conocedor esperaría: separan Las Cañitas de Palermo
Hollywood, aíslan un corredor real en Chacarita, identifican el Barrio Chino dentro de
Belgrano. Los desajustes que aparecen (San Telmo, parte de Avenida Corrientes, Caseros/
Barracas) tienen una explicación consistente: **el contenedor de macrozona (derivado de la
semilla, no de un polígono editorial real) es el eslabón más débil**, no el algoritmo de
clustering.

## ¿Dónde funciona muy bien?

- **Chacarita.** El problema histórico de la Tanda 2 (un solo hull convexo de 1.546 ha)
  queda resuelto: 7 clusters compactos y separados, con un corredor limpio y creíble
  (C0, 34 locales, forma lineal evidente). Ningún indicio de fusión ni de fragmentación
  excesiva.
- **Las subzonas chicas de Palermo** (Las Cañitas, Palermo Chico, Palermo Nuevo/Botánico):
  los clusters HDBSCAN caen dentro o muy cerca de las elipses editoriales correspondientes,
  sin que el pipeline haya usado esa capa como insumo (es pura coincidencia geográfica
  entre densidad de datos y demarcación editorial, que es exactamente lo que se buscaba).
- **Villa Crespo** como caso neutro: 9 clusters bien separados, sin fusiones ni
  fragmentación aparente, sin ninguna referencia editorial que "ayude" — el resultado se
  sostiene solo.
- **Microcentro y Corrientes, después de la segunda pasada** (Etapa V2-4): lo que
  aparecía como "todo es denso" se convierte en 10-11 focos concretos y espacialmente
  separados. Es el resultado más útil de todo el prototipo para un informe editorial.

## ¿Dónde funciona aceptablemente (con matices)?

- **Belgrano.** El núcleo dominante (88 locales) es real, pero probablemente mezcla tres
  identidades editoriales (Barrio Chino, Cabildo/Juramento, Bajo Belgrano). La segunda
  pasada solo logra recuperar 3 sub-grupos y descarta como ruido a casi dos tercios de los
  puntos (61 %): la subdivisión es posible pero no automática con los parámetros
  actuales — un cluster alargado y de densidad decreciente necesita un tratamiento propio.
- **Avenida Corrientes.** El corredor central (C5, 128 locales) es correcto y bien
  formado. Pero el segundo cluster grande (C7, 133 locales, en San Nicolás) queda **fuera**
  de la elipse editorial "Corrientes 9 de Julio-Callao", que aparece vacía en el mapa. No
  hay forma de saber, sin revisión de terreno, si el contenedor de macrozona se pasó de
  ancho (absorbiendo San Nicolás como si fuera Corrientes) o si la oferta real está
  efectivamente más al este del eje oficial.
- **San Telmo, núcleo periférico.** El racimo alrededor del Mercado funciona bien; pero dos
  clusters (C4 al norte, C1 al sur) caen claramente fuera de todas las elipses editoriales
  de San Telmo — el contenedor los incluyó, la identidad editorial probablemente no.

## ¿Dónde falla?

- **Costanera Norte: fallo total, pero del tipo correcto.** Solo 2 entidades del universo
  V1 caen en el contenedor; el pipeline dice "sin evidencia suficiente" en vez de inventar
  un núcleo. Es una falla de **datos**, no de método, y el pipeline la declara en vez de
  disimularla — el comportamiento deseable.
- **Avenida Caseros / Barracas: confianza baja por diseño débil del contenedor**, no del
  clustering. Con solo 1 punto semilla sobreviviente tras depurar apartados, el hull del
  contenedor es casi un punto: cualquier resultado que salga de ahí es, en el mejor caso,
  ilustrativo, no confiable.
- **Belgrano C2 en la segunda pasada** (no en la Etapa 3): forzar `leaf + epsilon=25 m`
  sobre un cluster alargado poda en vez de subdividir. Es una falla de la técnica de
  segunda pasada tal como está parametrizada hoy, no del detector original.

## ¿Por qué falla? (causas raíz, no síntomas)

1. **El contenedor de macrozona es una aproximación derivada de 3-19 puntos semilla**, no
   un polígono editorial real. Es la causa directa de los tres desajustes de "sector fuera
   de zona" (San Telmo C4/C1, posiblemente Corrientes C7) y del caso de baja confianza
   (Caseros/Barracas). Ya estaba señalado como el supuesto más frágil del prototipo
   (informe final V1, §3.1); esta validación lo confirma con casos concretos, no en
   abstracto.
2. **La segunda pasada usa un solo epsilon fijo (25 m) para todos los clusters
   sobredimensionados**, sin distinguir forma. Funciona en clusters compactos y de
   densidad pareja (Microcentro, Palermo); poda en clusters alargados y de densidad
   decreciente (Belgrano).
3. **Evidencia escasa o sesgada en ciertas franjas** (Costanera Norte, Caseros/Barracas):
   no hay suficiente F01/F02 georreferenciado en esas zonas para que ningún método de
   clustering encuentre estructura real, exista o no.

## Qué patrones aparecen (Etapa V2-5, tipología)

Emergen **5 categorías reales**, no forzadas: multi-núcleo (7 de 12 macrozonas — el
comportamiento más común y el mejor resuelto), núcleo dominante + satélites (2 casos,
justo las que generan clusters sobredimensionados), polo disperso (Puerto Madero), y dos
casos de evidencia/confianza insuficiente. Ningún caso es "corredor puro": los corredores
detectados (Corrientes, Chacarita, Palermo) siempre conviven con núcleos no lineales
dentro de la misma macrozona — el corredor es una propiedad de un cluster, no de una
macrozona completa.

## Qué mejoras serían realmente necesarias (antes de V2)

En orden de impacto esperado:

1. **Contornos editoriales reales de los 12 polos** (reemplazar el hull de semilla +
   buffer). Resuelve de raíz los tres desajustes de "fuera de zona" identificados y baja
   directamente la incertidumbre de Caseros/Barracas.
2. **Segunda pasada condicionada a la forma del cluster**: aplicar `leaf + epsilon chico`
   solo si el cluster sobredimensionado es compacto (compacidad y elongación dentro de
   rango); para clusters alargados, usar un epsilon mayor o directamente no forzar
   subdivisión y tratarlo como corredor extendido.
3. **Revisión de terreno puntual en Avenida Corrientes**: confirmar si San Nicolás debe
   contarse como parte de la macrozona "Corrientes" o si el contenedor se pasó de ancho —
   ningún dato adicional resuelve esto, requiere criterio editorial.
4. **Tratamiento diferenciado por tipología** (Etapa V2-5): a las macrozonas de evidencia
   insuficiente o contenedor de baja confianza, no forzarles un resultado de microzonas;
   marcarlas explícitamente como pendientes de más datos.

Ninguna de estas mejoras requiere cambiar el detector principal (HDBSCAN core): son
ajustes en los insumos (contornos) y en cuándo/cómo aplicar la segunda pasada.
