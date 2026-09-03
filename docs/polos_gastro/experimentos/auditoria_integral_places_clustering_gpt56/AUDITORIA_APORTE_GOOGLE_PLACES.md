# Auditoría del aporte de Google Places

## Veredicto

**Hecho verificado.** Places amplió materialmente la cobertura dentro de las 13 macrozonas: aporta 3.221 de 6.461 puntos (49,9 %). Su aporte no es homogéneo. Varía de 31,0 % en Microcentro a 93,1 % en Costanera Norte.

**Inferencia.** Places corrige huecos visibles de F01/F02, especialmente donde F02 no representa bien la oferta comercial a la calle. También cambia la estructura del clustering en 10 de 13 macrozonas bajo la comparación HDBSCAN cruda utilizada en esta auditoría. Por lo tanto, no funciona sólo como aumento de volumen.

**Recomendación.** Mantener Places como capa auxiliar explícita, nunca como padrón ni como prueba de actividad. No promover a mapa principal unidades con más de 60 % Places sin corroboración adicional y decisión humana.

## Números verificados

| Concepto | Resultado | Fuente local |
| --- | ---: | --- |
| Consultas piloto planificadas | 379 | `plan_consultas_places.csv` |
| Resultados piloto sanitizados | 3.511 | `places_sanitizado.csv` |
| Nuevos piloto bajo reglas del piloto | 1.651 | `qa_universo_piloto.json` |
| Consultas ampliación A | 351 | `plan_consultas_a_criticas.csv` |
| Consultas ampliación B | 260 | `plan_consultas_b_consolidacion.csv` |
| Consultas de refino Chacarita | 18 | `plan_refino_chacarita_saturadas_3x3.csv` |
| Resultados brutos acumulados por origen | 6.208 | `qa_integracion_completa_v1.json` |
| Fuera de macrozona | 983 | mismo QA |
| Repetidos por identificador entre tandas | 146 | mismo QA |
| Duplicados contra F01/F02 | 1.858 | mismo QA |
| Places nuevos acumulados | 3.221 | mismo QA |
| Universo final | 6.461 | CSV y GeoJSON coincidentes |

La corrida completa atribuye 1.684 puntos al origen piloto, no 1.651. No es doble conteo: los IDs finales son únicos. Es una discrepancia de reglas/contención entre dos corridas y debe documentarse antes del informe.

## Dependencia territorial

- Dependencia alta: Costanera Norte 93,1 %; Puerto Madero 71,1 %; Caseros/Barracas 69,0 %; Chacarita 65,5 %; Villa Crespo 60,5 %; Caballito 60,4 %.
- Dependencia media: Belgrano 56,4 %; Recoleta 47,3 %; San Telmo 46,6 %; Palermo Soho 44,6 %; Palermo Hollywood 41,0 %.
- Dependencia baja relativa: Corrientes 39,9 % y Microcentro 31,0 %.

Todos los 163 microclusters finales contienen al menos un punto Places. Esto muestra penetración completa de la fuente en la salida, no validación independiente.

## Saturación y subcaptura

**Hecho verificado.** Tanda A registró 2 celdas saturadas en Chacarita; ambas recibieron refino 3x3. Tanda B dejó 58 celdas con 20/20 resultados: 19 en Villa Crespo, 29 en Recoleta y 10 en Caballito. No existe refino almacenado para esas 58 celdas.

**Inferencia.** En esas tres zonas, 404/363/274 puntos Places son un piso condicionado por el límite de respuesta por celda. La dependencia Places puede estar subestimada y la forma local puede estar distorsionada por subcaptura diferencial.

## Contención geométrica

La integración descarta 983 resultados fuera de las macrozonas. La regla evita que sedes lejanas deformen el universo, pero vuelve el resultado condicionado por contenedores editoriales previos. Un punto inmediatamente fuera no puede generar una nueva concentración. Este mecanismo sirve para estudiar zonas conocidas; no sirve para descubrir polos fuera de ellas.

## Sesgo de fuente

Places mide oferta visible en una plataforma comercial. Puede sobrerrepresentar áreas turísticas, negocios con mayor huella digital y categorías bien indexadas. La auditoría no puede medir recall absoluto porque no existe padrón contemporáneo de locales operando.

## Resultado por zona

El detalle reproducible se encuentra en `diagnostico_places_por_zona.csv`. La clasificación “cambio estructural” compara HDBSCAN completo contra F01/F02 solamente, antes de KMeans; no equivale por sí sola a una mejora.

