# Casas de pastas en CABA — Padrón candidato integrado (v2)

_Fecha: 2026-06-20 · Versión v2 · **Padrón candidato no oficial, pendiente de validación manual.**_

> Se construyó un padrón candidato integrado de **261** posibles casas de pastas en CABA, combinando registro oficial, fuentes abiertas y señales operativas no oficiales. El resultado no reemplaza al registro oficial ni constituye un censo definitivo: sirve como base analítica para validación territorial.

## Resumen ejecutivo

- **261** candidatos únicos.
- **180** independientes / de barrio · **81** en cadenas.
- **53** multifuente (≥2 fuentes).
- **42** pendientes de validación manual.

## Fuentes y capas

| Fuente | Naturaleza | Detectados | Qué puede / no puede afirmar |
|---|---|---|---|
| AGC / F02 | Registro administrativo **oficial** | 11 | Habilitaciones; **no implica local activo** |
| OpenStreetMap | Relevamiento **abierto auxiliar** | 152 | Cobertura territorial; **no oficial** |
| Google Places | **Operativa no oficial** | 151 | Visibilidad comercial; **no gubernamental** |
| Integrado v2 | **Padrón candidato** | 261 | Unión deduplicada; **a validar** |

_Detectados por fuente dentro del padrón integrado post-deduplicación; no equivale a resultados brutos._

## Clases integradas

- Multifuente: 36 · Google: 70 · OSM: 102 · AGC oficial estricto: 11 · Revisión manual: 42

## Distribución territorial

- **Top comunas:** 14 (33), 13 (33), 6 (25), 12 (24), 2 (22).
- **Top barrios:** Palermo (33), Caballito (25), Recoleta (22), Belgrano (22), Villa Urquiza (19).
- **Densidad comuna (cand./km²):** 6 (3.65), 2 (3.42), 5 (3.00), 13 (2.22), 14 (2.07).
- **Densidad barrio (cand./km²):** Almagro (4.20), Caballito (3.65), Colegiales (3.49), Villa Urquiza (3.49), Recoleta (3.42). No es densidad por habitante.

## Cadenas e independientes

No es un informe de franquicias: **180** independientes. Principales cadenas (control de cobertura): la juvenil (28), multipasta (7), caprizzi (4), master pastas / pastas master (2), milena pastas artesanales (2), pastas mazzeo (2).

## Control de calidad

- La Juvenil: 28 sucursales = unión de fuentes (19 Google + 19 OSM, 10 en común); las solo-OSM están a >600 m de cualquier Google → locales distintos, no duplicados.
- Cadenas auditadas: 11 · sin alertas de inflación.
- Posibles duplicados: 2 (resultaron distintos) · falsas fusiones: 0.
- 4 casos `revisar_fusion` resueltos: 2 fusionados con su A, 1 descartado (bodegón), 1 mantenido en B.

## Limitaciones

- No es censo definitivo ni padrón oficial. Google/OSM no son oficiales. AGC es oficial pero angosto y no implica local activo. Puede haber locales cerrados o faltantes. Falta validación manual/campo.

## Próximos pasos

1. Validar los 42 casos manuales.
2. Revisar independientes prioritarios.
3. Confirmar multifuente.
4. Incorporar al pipeline solo tras validación.
5. Replicar la metodología en otros rubros.
