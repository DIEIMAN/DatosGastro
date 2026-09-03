# QA de las 4 macrozonas corregidas (Etapa Cal-4)

**Fecha:** 2026-07-08 · Corrido con `qa_correcciones_bloqueantes.py`, que reconstruye
`macrozonas_v1_experimental` reemplazando **solo** Microcentro, Belgrano, Costanera Norte
y Chacarita por sus versiones corregidas, y audita esa capa hipotética contra sus vecinas.

## 1. Validez geométrica y huecos

Las 4 geometrías corregidas son válidas y sin huecos interiores. Sin gates duros.

## 2. Solapamientos

| Par | % del área menor | Entidades en el solape | Lectura |
|---|---|---|---|
| **Avenida Corrientes × Microcentro** | — (resuelto) | 0 | El bloqueante #1 queda resuelto: de 49,2 % a 0. |
| Palermo Hollywood × Chacarita | 7,2 % | 4 | Menor; ambas macrozonas son vecinas geográficas reales (Chacarita linda con Palermo). No es un problema nuevo grave, pero queda para revisión. |
| Palermo (contextual) × Costanera Norte | 75,1 % (subió de 67,8 %) | 3 | Palermo a nivel de polo **no es contenedor de clustering** (`es_contenedor_clustering=false`): impacto operativo bajo, igual que antes. Subió porque Costanera Norte se achicó hacia la zona que más se solapa con Palermo. |

**El bloqueante prioritario (Corrientes/Microcentro) queda completamente resuelto**, sin
introducir ningún solapamiento nuevo de magnitud comparable.

## 3. Entidades duplicadas

**0 entidades en 2+ macrozonas-contenedor de clustering** (antes de esta corrección: 406,
solo por el par Corrientes/Microcentro). Resuelto en su totalidad.

## 4. Entidades fuera de contenedor (huérfanas tras la corrección)

| Macrozona | Entidades perdidas | Entidades ganadas | De las perdidas, sin ninguna macrozona |
|---|---|---|---|
| Microcentro y Centro | 406 | 0 | **0** (las recupera Avenida Corrientes) |
| Belgrano | 53 | 84 | **53** ⚠️ |
| Costanera Norte | 0 | 0 | 0 |
| Chacarita | 0 | 0 | 0 |

**Hallazgo a resolver antes de aprobar Belgrano:** el corredor de 3 avenidas (Juramento/
Libertador/Cabildo) gana 84 entidades nuevas respecto de las elipses viejas, pero **pierde
53 que quedan sin ninguna macrozona** — las elipses de fase16, aunque dibujadas a mano,
cubrían zonas del barrio que el corredor de avenidas no alcanza (probablemente manzanas a
media cuadra de las 3 avenidas, fuera del semiancho de 250 m). Antes de aprobar esta
corrección, alguien de DGDGAS debería revisar esas 53 entidades puntualmente: si son
locales reales de Barrio Chino/Bajo Belgrano/Belgrano R, el semiancho de 250 m se queda
corto y conviene subirlo (con el costo de superficie que eso implica) o volver a un
método híbrido (corredor + un buffer menor sobre las elipses viejas como respaldo).

## 5. Cobertura de CABA

**Bajó de 19,66 % a 12,19 %** (macrozonas nivel polo, contenedores de clustering). Es
consecuencia esperada de que 3 de las 4 correcciones **redujeron** superficie (Microcentro
−49 %, Costanera Norte −33 %, Chacarita −16 %) y solo Belgrano creció (+15 %, pero no lo
suficiente para compensar). No es un defecto en sí — las macrozonas más chicas son más
honestas respecto de dónde hay evidencia real — pero es una baja notable que vale la pena
que Diego tenga presente: **la superficie total "cubierta" por macrozonas editoriales cae
significativamente** cuando se prioriza precisión sobre cobertura.

## Conclusión de la Etapa Cal-4

El bloqueante #1 (Corrientes/Microcentro) se resuelve limpio, sin efectos colaterales
serios. Costanera Norte y Chacarita mejoran sin generar nuevos problemas. **Belgrano
mejora en trazabilidad pero introduce un trade-off real (53 entidades huérfanas) que debe
quedar explícito en la revisión humana**, no aprobarse a ciegas junto con las otras 3.
