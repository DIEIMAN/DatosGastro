# Decisión técnica territorial V3

## Resultado técnico

- Belgrano: **BEL-A**, unidad macro multiparte con tres centralidades internas.
- Recoleta: **REC-A**, unidad general con centralidades analíticas internas.
- Costanera Norte: **CN-DEC10**, cuatro componentes discontinuos, incluido `CN_C02`.

## Evidencia documental

Se usó exclusivamente para contraste, denominación y caracterización post hoc. No fue feature,
semilla ni restricción de clustering.

## Decisión institucional vigente

Belgrano y Recoleta son un polo cada uno. DEC-10 cierra la adopción de Costanera Norte y la
inclusión de sus cuatro componentes. No se reescala esa decisión.

## Recomendación del cartógrafo

Adoptar BEL-A, REC-A y CN-DEC10. Conservar BEL-C y REC-B como alternativas de respaldo.

## Decisiones que requieren a Diego

Ninguna bloquea el handoff. Solo requeriría firma humana promover Belgrano R de
`SECTOR_SECUNDARIO` a `SUBPOLO_INTERNO`. La recomendación actual es **no promoverlo**.

| polo | modelo | cobertura | estabilidad | continuidad | compacidad | dependencia_fuente | claridad_institucional | riesgo_fragmentacion | riesgo_union_artificial | respaldo_documental | recomendacion | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BELGRANO | BEL-A | 35.58 | 0.765 | 0.606 | 0.093 | 53.23 | ALTA | BAJO | BAJO | POST_HOC | SI | Mejor equilibrio: tres centralidades emergen a 160 m sin hull común. |
| BELGRANO | BEL-B | 29.56 | 0.719 | 0.654 | 0.116 | 53.4 | MEDIA | ALTO | MEDIO | POST_HOC | NO | A 120 m aparecen seis fragmentos; elegir cuatro sería arbitrario. |
| BELGRANO | BEL-C | 33.57 | 0.765 | 0.606 | 0.061 | 53.42 | MEDIA | MEDIO | BAJO | POST_HOC | RESPALDO | Conserva toda la multiparte, pero comunica menos jerarquía interna. |
| RECOLETA | REC-A | 78.49 | 0.626 | 1.0 | 0.102 | 46.51 | ALTA | BAJO | BAJO | POST_HOC | SI | Los nueve núcleos forman una red continua; unidad general más parsimoniosa. |
| RECOLETA | REC-B | 78.36 | 0.613 | 0.959 | 0.092 | 46.59 | MEDIA | MEDIO | BAJO | POST_HOC | RESPALDO | Dos subzonas son posibles, pero agregan una división no imprescindible. |
| RECOLETA | REC-C | 78.23 | 0.626 | 1.0 | 0.067 | 46.67 | MEDIA | MEDIO | BAJO | POST_HOC | NO | La multiparte no mejora la lectura porque la red analítica ya es continua. |
| COSTANERA_NORTE | CN-DEC10 | 98.61 | 0.77 | 0.605 | 0.083 | 92.96 | ALTA | NO_APLICA_DECISION_CERRADA | BAJO | DEC-10_Y_POST_HOC | SI_DECISION_VIGENTE | DEC-10 fija cuatro componentes y preservación de vacíos. |
