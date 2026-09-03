# Comparación: contenedores anteriores (hull-de-semilla) vs. macrozonas_v1_experimental

**Fecha:** 2026-07-08 · Prueba de pipeline (Tarea 6), sobre 2 casos: Palermo Soho/Hollywood
(reconfirmación de la Etapa Infra-4) y Avenida Corrientes (caso nuevo). Mismo detector,
mismos parámetros HDBSCAN que el prototipo V1 — solo cambia el contenedor de entrada.

## Caso A — Palermo Soho / Palermo Hollywood (control de consistencia)

Ya evaluado en detalle en la Etapa Infra-4. Esta tanda solo reconfirma que la capa final
`macrozonas_v1_experimental.geojson` reproduce exactamente los mismos números: **373
entidades en Palermo Soho, 213 en Palermo Hollywood** (coincide con Infra-4). Conclusiones
ya documentadas ahí: el contorno real separa Soho de Hollywood de raíz, pero no elimina
por sí solo el núcleo sobredimensionado interno de Soho (sigue necesitando la segunda
pasada, con su costo de ruido ya conocido).

## Caso B — Avenida Corrientes (nuevo)

| | Contenedor anterior (hull-de-semilla) | macrozonas_v1 (corredor real) |
|---|---|---|
| Entidades en el contenedor | 860 (dato del prototipo V1) | **754** |
| Entidades compartidas entre ambos mundos | 351 (41 % del contenedor viejo, 47 % del nuevo) | — |
| Clusters HDBSCAN | 9 | 10 |
| Clusters sobredimensionados (>35 ha) | 1 (C7, 133 locales/46,5 ha) | **0** |
| Ruido | 29,2 % | 25,2 % |

El contenedor viejo y el corredor nuevo se solapan poco más de un tercio: cada uno cubre
territorio real que el otro no cubre (ver mapa). No es que uno sea estrictamente mejor en
volumen — el hallazgo relevante es **cuál** territorio cubre cada uno (siguiente sección).

### Hallazgo principal: el contenedor viejo dejaba fuera casi un tercio de la avenida real

El mapa comparativo (`comparativo_mundo_a_vs_b_avenida_corrientes.png`) muestra algo muy
concreto: en el panel "ANTES", **todo el tramo este de la avenida (hacia San Nicolás)
aparece en gris** — no porque HDBSCAN lo marcara como ruido, sino porque esas entidades
**ni siquiera estaban dentro del contenedor viejo** (hull de la semilla de
Corrientes+Abasto). El contenedor anterior, construido con apenas 13 puntos semilla,
subestimaba dónde llega realmente la avenida. Esto **confirma con datos concretos** el
hallazgo de la validación anterior (Etapa V2-3): *"la elipse editorial 'Corrientes 9 de
Julio-Callao' quedaba vacía, y el cluster más grande caía en San Nicolás, fuera de esa
elipse"* — no era que el cluster estuviera mal puesto, era que el contenedor no llegaba
hasta ahí.

### El corredor real también resuelve, en este caso, el problema del núcleo sobredimensionado

A diferencia de Palermo Soho (donde el contorno real no bastó y siguió apareciendo un
cluster de 251 locales), en Avenida Corrientes **el corredor real por sí solo eliminó el
cluster sobredimensionado** (0 de 10 clusters supera 35 ha). Hipótesis: un corredor
angosto (semiancho 350 m) fuerza naturalmente una segmentación en tramos porque HDBSCAN
no tiene margen lateral para fusionar núcleos que en Soho sí tenía (un polígono más
"gordo" y compacto). Esto sugiere que **la forma del contenedor (angosto vs. compacto)
importa tanto como su precisión** — un hallazgo nuevo que no estaba en la validación
anterior.

### Lo que no cambia: el ruido sigue siendo del orden del 25-29 %

El corredor real no "limpia" el ruido de forma dramática — pasa de 29 % a 25,2 %, una
mejora modesta. Gran parte del ruido son entidades dispersas a lo largo de la avenida sin
suficiente densidad local para formar cluster, lo cual es información real (oferta
dispersa existe), no un defecto del contorno.

## Síntesis de la Tarea 6

| Pregunta | Respuesta |
|---|---|
| ¿El contorno real mejora sobre el contenedor anterior? | **Sí, en ambos casos**, pero de formas distintas: en Palermo separa identidades mezcladas; en Corrientes incorpora territorio real que el contenedor viejo no alcanzaba a cubrir y además evita el cluster sobredimensionado. |
| ¿Elimina todos los problemas de la validación? | No todos: Palermo Soho sigue necesitando segunda pasada. Pero **cero** problemas nuevos aparecieron que no existieran antes — todo cambio fue una mejora o un problema ya conocido (el solapamiento Corrientes/Microcentro, que es un problema de **frontera entre dos macrozonas**, no de la calidad interna de ninguna de las dos). |
| ¿Vale la pena avanzar con esta capa? | Sí, con la condición de resolver el solapamiento Corrientes/Microcentro antes de una corrida completa (ver `QA_MACROZONAS_V1.md`). |
