# Metodologia - Capa objetiva Fase 8 fuerte

Fecha de consulta: 2026-07-01.

## Objetivo

Construir una capa objetiva de contexto territorial para contrastar la lectura documental de
PolosGastro con datos abiertos u oficiales disponibles localmente. La capa es un insumo tecnico:
no es ranking, no delimita polos y no modifica clasificaciones.

## Fuentes usadas

- F01 - `data/raw/f01_oferta_establecimientos_gastronomicos.csv`: 2823 registros de oferta
  gastronomica registrada.
- F02 procesada - `data/processed/fact_habilitacion_gastronomica.csv`: 44169 habilitaciones
  gastronomicas historicas.
- `data/processed/dim_ubicacion.csv`: apoyo para comuna normalizada de F02.
- `outputs/polos_gastro/fase7/tablas/tabla_polos_para_informe_borrador_2.csv`: universo de 32
  registros territoriales de Borrador 2, solo lectura.
- `outputs/polos_gastro/fase5/polos_gastro_universo_consolidado_fase5.csv`: barrios y comunas de
  referencia, solo lectura.

No hubo descargas nuevas.

## Campos usados

F01:

- `barrio`
- `comuna`
- `id`
- `categoria`

F02 procesada:

- `id_habilitacion`
- `id_ubicacion`
- `anio_fuente`
- `fecha_habilitacion`
- `categoria_gastronomica_inferida`

Dimension ubicacion:

- `id_ubicacion`
- `comuna`
- `barrio`
- `calidad_geo`

## Agregacion

- Oferta registrada por barrio: conteo de registros F01 por `barrio` y `comuna`.
- Oferta registrada por comuna: conteo de registros F01 por `comuna`.
- Habilitaciones por comuna: conteo de registros F02 por comuna normalizada desde
  `dim_ubicacion`.
- Habilitaciones por barrio: no se calcula. En F02, 44099 registros quedan sin barrio
  util o determinado, por lo que la lectura barrial no es robusta.
- Habilitaciones sin comuna determinada luego del cruce: 1050 registros.

## Cortes temporales

F02 permite una lectura aproximada por `anio_fuente`. Se calcula:

- total historico disponible 2015-2025;
- ultimos 5 anios de fuente, aproximados como 2021-2025;
- ultimos 10 anios, solo como aproximacion 2015-2025 porque el bloque 2015-2018 no puede
  separarse con precision uniforme.

## Indice de senal objetiva

El `indice_senal_objetiva` es un indicador interno de 0 a 100.

- Por barrio: normaliza la cantidad de oferta registrada F01 contra el maximo barrial observado.
- Por comuna: promedia dos senales normalizadas, F01 oferta registrada y F02 habilitaciones
  historicas.

El indice significa presencia relativa en las fuentes disponibles. No significa densidad real,
vigencia operativa, calidad gastronomica, importancia institucional ni delimitacion oficial.

## Limites

- F01 es una fuente de oferta registrada; no prueba que los establecimientos sigan abiertos.
- F02 mide habilitaciones aprobadas historicas; no equivale a locales activos.
- La lectura por comuna es mas estable pero menos precisa para corredores y subpolos.
- La lectura por barrio no resuelve calles, ejes ni bordes.
- Los corredores requieren una delimitacion territorial previa para evitar comparaciones falsas.
- Palermo, Belgrano, Corrientes, Abasto, DoHo, Costanera Norte, Avenida Caseros y Federico Lacroze
  requieren tratamiento especial por subpolos, solapamientos o recorridos.
- No se usa Google Places porque la fase debe basarse en fuentes abiertas/oficiales locales y no
  en APIs privadas o datos crudos de plataformas.
- No se generan delimitaciones oficiales porque la capa es solo contexto.
