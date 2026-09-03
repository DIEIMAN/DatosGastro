# Recomendación de camino para un Pipeline V2 (Etapa V2-7)

**Fecha:** 2026-07-08 · **Carácter:** recomendación, no implementación. Se apoya en la
evidencia de las Etapas V2-1 a V2-6 (casos reales, no hipótesis). Nada de esto se corre
todavía.

## Punto de partida

El prototipo V1 ya demostró que el enfoque funciona: HDBSCAN intra-macrozona sobre el
universo F01+F02 produce microzonas creíbles en la mayoría de los casos (informe de
validación metodológica: sí, salvo casos puntuales, con causa identificada). **V2 no debe
ser "probar otro algoritmo"**: el detector central no fue la fuente de ningún fallo
observado. V2 debe cerrar las tres brechas concretas que esta validación encontró.

## Cambios que sí valen la pena

### 1. Contornos editoriales reales (prioridad máxima)
Reemplazar el contenedor "hull de semilla + buffer 500 m" por una digitalización real de
los 12 polígonos de polo (una vez, a mano o semi-asistida sobre el callejero GCBA). Es el
cambio de mayor impacto: resuelve directamente los tres desajustes de "cluster fuera de
zona editorial" (San Telmo C4/C1, la ambigüedad de Corrientes/San Nicolás) y transforma
Caseros/Barracas de "baja confianza" a un resultado evaluable. Sin este cambio, cualquier
otra mejora sigue construida sobre una base aproximada.

### 2. Segunda pasada condicionada a la forma, no un epsilon único
La Etapa V2-4 mostró que `leaf + epsilon=25 m` funciona en clusters compactos (Microcentro,
Palermo: 10-11 focos útiles) pero poda en clusters alargados de densidad decreciente
(Belgrano: pierde el 61 % como ruido). V2 debería decidir automáticamente la estrategia de
segunda pasada según la forma del cluster original (compacidad/elongación ya calculadas en
la Etapa 5): epsilon chico + leaf para compactos; para alargados, o un epsilon mayor, o
tratarlos directamente como corredor extendido en vez de forzar sub-núcleos.

### 3. Tratamiento diferenciado por tipología (Etapa V2-5)
Las 5 categorías que emergieron (multi-núcleo, núcleo dominante+satélites, disperso,
evidencia insuficiente, contenedor de baja confianza) no deberían recibir el mismo
pipeline ciego. Concretamente: a las de evidencia insuficiente o contenedor degradado, no
entregarles microzonas — marcarlas "pendiente de más datos" en vez de forzar un resultado
que nadie puede evaluar con confianza (Costanera Norte, Caseros/Barracas).

## Cambios que NO valen la pena todavía

- **Cambiar el detector principal.** HDBSCAN no fue la causa de ningún desajuste
  observado; los tres problemas encontrados son de insumos (contornos) y de la técnica de
  segunda pasada, no del algoritmo base.
- **Bajar parámetros globales para "encontrar más corredores".** Villa Crespo C6 sugiere
  que el umbral de corredor puede ser un poco estricto, pero es un ajuste fino de un
  umbral, no un cambio de enfoque — se calibra en el piloto, no se rediseña.
- **Incorporar Google Places como fuente de puntos.** Nada en esta validación señala que
  el problema sea volumen o cobertura de puntos; el problema es la geometría del
  contenedor y el tratamiento de clusters grandes. Places sigue en su rol ya definido
  (validación de vigencia por muestreo), no como insumo de esta mejora.
- **Rehacer la deduplicación del universo.** No apareció ningún caso donde un cluster
  pareciera inflado por duplicados; los desajustes fueron todos territoriales.

## Orden sugerido

1. Digitalizar los 12 contornos editoriales (una vez, esfuerzo acotado — no requiere
   recorrer el pipeline).
2. Re-correr las Etapas 3-5 del prototipo V1 sin cambiar ningún parámetro de clustering,
   solo con los contornos nuevos, y repetir la validación visual (Etapas V2-2 y V2-3) para
   confirmar que los tres desajustes desaparecen.
3. Implementar la segunda pasada condicionada a forma (punto 2 arriba) y volver a correrla
   sobre los mismos 6 clusters sobredimensionados para comparar.
4. Recién ahí, con contornos reales y segunda pasada ajustada, tiene sentido plantear una
   corrida completa versionada (Fase D del plan de adopción original) para que Diego
   revise microzonas candidatas a nivel de toda la ciudad.

Este orden prioriza cerrar brechas de insumos antes de escalar: correr la Fase D completa
hoy repetiría los mismos tres desajustes en las macrozonas que todavía no se validaron
visualmente (Caballito, Recoleta, Puerto Madero, Microcentro).
