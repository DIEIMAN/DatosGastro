# Auditoría de deduplicación

## Veredicto

**Hecho verificado.** La resolución F01/F02 reduce 41.010 filas gastronómicas filtradas a 9.739 entidades. F02 se colapsa a 7.866 ubicaciones; 814 se fusionan con F01. En Places, la integración elimina 146 repeticiones entre tandas y 1.858 coincidencias contra F01/F02 antes de incorporar 3.221 puntos.

**Inferencia.** Las reglas son razonables como primera resolución automática, pero no están calibradas contra una muestra etiquetada. El universo final conserva una cola importante de colocalizaciones o duplicados residuales posibles.

## Reglas auditadas

- F01: mismo nombre e ubicación, o mismo nombre a 40 m.
- F02: una entidad por `id_ubicacion`.
- F01/F02: misma ubicación, misma dirección o hasta 15 m con categoría compatible; 15-30 m se marca para revisión.
- Places/Places: identificador interno entre tandas.
- Places/F01+F02: hasta 15 m sin exigir nombre, o hasta 40 m con nombre compatible.
- Compatibilidad de nombre Places: inclusión de cadena o intersección de al menos 50 % de tokens respecto del nombre más corto.

## Hallazgos

1. **No hay IDs finales repetidos** y no hay pares cruzados Places/F01-F02 a 15 m o menos: la regla los eliminó.
2. **844 filas** participan en coordenadas exactas repetidas y existen **755 pares** a distancia prácticamente cero. Son principalmente colocalizaciones dentro de una misma fuente. No todos son duplicados: pueden ser galerías, mercados o múltiples habilitaciones/entidades en una parcela.
3. Dentro de 40 m hay **10.410 pares**. La cola automática marca 2.217 como falsos negativos probables por compatibilidad de nombre. Esta cifra es un máximo de revisión, no un conteo confirmado.
4. Entre los Places retenidos, 0 % queda a 15 m de la base, 16,5 % a 20 m, 38,7 % a 30 m y 54,5 % a 40 m. El salto muestra alta sensibilidad espacial justo después del umbral duro.
5. `sjoin_nearest` conserva un único vecino más cercano. Si el más cercano tiene nombre incompatible pero un segundo vecino a 40 m es compatible, el duplicado puede no detectarse.
6. Colapsar F02 por ubicación evita inflación administrativa, pero también puede fusionar comercios diferentes en una dirección compartida.

## Riesgos

- Falso positivo: dos negocios distintos en la misma parcela se fusionan a 15 m aunque sus nombres difieran.
- Falso negativo: variantes ortográficas o nombres genéricos no alcanzan el 50 % de tokens.
- Sucursales: la regla F01 de mismo nombre a 40 m puede fusionar locales próximos de una cadena.
- Sin nombre: F02 no permite resolver establecimientos múltiples dentro de una ubicación.
- Densidad: los falsos negativos elevan densidad y pueden crear puentes; los falsos positivos reducen densidad y pueden romper núcleos.

## Prueba recomendada antes del informe

Etiquetar manualmente una muestra estratificada y anónima de 150-250 pares: distancia 0-5, 5-15, 15-30 y 30-40 m; misma/cruzada fuente; nombre compatible/incompatible; zonas densas y corredores. Estimar precisión y recall de la regla. No cambiar umbrales antes de esa prueba.

La muestra publicable `muestra_casos_deduplicacion_revision.csv` no contiene nombres, IDs ni coordenadas. `sensibilidad_umbral_deduplicacion.csv` contiene sólo agregados.

