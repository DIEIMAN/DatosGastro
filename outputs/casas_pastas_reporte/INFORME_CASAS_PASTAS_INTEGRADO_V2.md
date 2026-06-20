# Casas de pastas en CABA — Padrón candidato integrado (V2 ejecutivo)

_Fecha: 2026-06-20 · Versión V2 · **Padrón candidato no oficial, pendiente de validación manual.**_

> El registro oficial muestra el núcleo administrativo estricto, pero el universo operativo probable de casas de pastas en la Ciudad es más amplio. El padrón candidato integrado combina AGC, OpenStreetMap y Google Places para construir una base analítica, no oficial, pendiente de validación manual.

## Indicadores

- **261** candidatos únicos · **180** independientes / de barrio · **81** en cadenas · **53** multifuente · **42** en revisión manual.

## Fuentes y capas

| Fuente | Naturaleza | Detectados | Qué puede / no puede afirmar |
|---|---|---|---|
| AGC / F02 | Registro administrativo **oficial** | 11 | Habilitaciones; **no implica local activo** |
| OpenStreetMap | Relevamiento **abierto auxiliar** | 152 | Cobertura territorial; **no oficial** |
| Google Places | **Operativa no oficial** | 151 | Visibilidad comercial; **no gubernamental** |
| Integrado v2 | **Padrón candidato** | 261 | Unión deduplicada; **a validar** |

_Detectados por fuente dentro del padrón integrado post-deduplicación; no equivale a resultados brutos._

## Distribución territorial

- **Comunas (cantidad):** 14 (33), 13 (33), 6 (25), 12 (24), 2 (22).
- **Barrios (cantidad):** Palermo (33), Caballito (25), Recoleta (22), Belgrano (22), Villa Urquiza (19).
- **Densidad comuna (cand./km²):** 6 (3.65), 2 (3.42), 5 (3.00), 13 (2.22), 14 (2.07).
- **Densidad barrio (cand./km²):** Almagro (4.20), Caballito (3.65), Colegiales (3.49), Villa Urquiza (3.49), Recoleta (3.42). No es densidad por habitante.

## Cadenas e independientes

> El informe no describe únicamente cadenas: la mayor parte del padrón candidato corresponde a casas independientes o de escala barrial (180 de 261).

Cadenas (control de cobertura): LA JUVENIL (28), MULTIPASTA (7), CAPRIZZI (4), MASTER PASTAS / PASTAS MASTER (2), MILENA PASTAS ARTESANALES (2), PASTAS MAZZEO (2), RAVIOLON (2).

## Núcleo multifuente

- 53 candidatos en más de una fuente (Google + OSM): base de mayor confianza.
- Combinaciones: solo OSM 99 · solo Google 98 · Google+OSM 53 · solo AGC 11.

## Control de calidad

- 11 cadenas auditadas, sin alertas de inflación. La Juvenil (28) = unión legítima de fuentes.
- Posibles duplicados: 2 (resultaron distintos) · falsas fusiones: 0.
- Nombres genéricos ('pastas frescas', 'pastificio', 'fábrica de pasta') reclasificados como independientes, no cadenas.
- 42 casos en revisión manual (parte del control de calidad).

## Casos emblemáticos (a validar documentalmente)

- **LA JUVENIL** — fundada el 1 de diciembre de 1959 (Colegiales); negocio familiar de tres generaciones. Fuentes: La Nación, El Cronista (caso documentado).
- Raviolón (1971, referencia secundaria) y Master Pastas (marca actual desde 1995) requieren confirmación; Biasatti es reciente (2020). Multipasta, Pastas Mazzeo y Caprizzi sin año verificable. Detalle en `fuentes_historicas_casas_pastas.csv`.
- _No se infiere antigüedad por fama; solo se afirma lo que tiene fuente verificable._

## Limitaciones

- No es censo definitivo ni padrón oficial. Google/OSM no son oficiales. AGC es oficial pero angosto y no implica local activo. Puede haber locales cerrados o faltantes. La deduplicación es heurística. Falta validación manual/campo.

## Próximos pasos

1. Validar los 42 casos manuales.
2. Revisar independientes prioritarios.
3. Confirmar multifuente.
4. Documentar emblemáticos con fuentes.
5. Incorporar al pipeline solo tras validación.
6. Replicar en otros rubros.
