# Casas de pastas en CABA — Padrón candidato integrado (V3 ejecutivo)

_Fecha: 2026-06-20 · Versión V3 · **Padrón candidato no oficial, pendiente de validación manual.**_

> El registro oficial muestra el núcleo administrativo estricto, pero el universo operativo probable de casas de pastas en la Ciudad es más amplio. El padrón candidato integrado combina AGC, OpenStreetMap y Google Places para construir una base analítica, no oficial, pendiente de validación manual.

## Indicadores

- **261** candidatos únicos · **180** independientes / de barrio · **81** en cadenas · **53** multifuente · **42** en revisión manual.

## 1. ¿Qué universo permite ver el cruce de fuentes?

261 candidatos únicos. No es un padrón oficial ni un censo definitivo: es una base analítica para validación territorial.

## 2. ¿Por qué el registro oficial no alcanza?

| Fuente | Naturaleza | Detectados | Qué puede / no puede afirmar |
|---|---|---|---|
| AGC / F02 | Registro administrativo **oficial** | 11 | Habilitaciones; **no implica local activo** |
| OpenStreetMap | **Abierta auxiliar** | 152 | Cobertura territorial; **no oficial** |
| Google Places | **Operativa no oficial** | 151 | Visibilidad comercial; **no gubernamental** |
| Integrado v2 | **Padrón candidato** | 261 | Unión deduplicada; **a validar** |

_Detectados por fuente dentro del padrón post-deduplicación; no equivale a resultados brutos._

## 3. ¿Dónde se concentran?

- **Comunas (cantidad):** 14 (33), 13 (33), 6 (25), 12 (24), 2 (22).
- **Barrios (cantidad):** Palermo (33), Caballito (25), Recoleta (22), Belgrano (22), Villa Urquiza (19).

## 4. ¿Qué cambia con la densidad por km²?

- **Densidad comuna (cand./km²):** 6 (3.65), 2 (3.42), 5 (3.00), 13 (2.22), 14 (2.07).
- **Densidad barrio (cand./km²):** Almagro (4.20), Caballito (3.65), Colegiales (3.49), Villa Urquiza (3.49), Recoleta (3.42). No es densidad por habitante; el ranking difiere del de cantidad absoluta.

## 5. ¿Qué barrios son polos? 

Palermo y Caballito lideran; Recoleta y Belgrano empatan en el tercer lugar (22 c/u). Mapas de zoom para Palermo, Caballito y Recoleta.

## 6. ¿Cadenas o casas de barrio?

> El universo candidato no está compuesto solo por franquicias: predominan las casas independientes y de escala barrial (180 de 261; 81 en cadenas).

## 7. Principales cadenas (control de cobertura)

LA JUVENIL (28), MULTIPASTA (7), CAPRIZZI (4), MASTER PASTAS / PASTAS MASTER (2), MILENA PASTAS ARTESANALES (2), PASTAS MAZZEO (2), RAVIOLON (2).

## 8. Núcleo de mayor confianza

- 53 candidatos multifuente (Google + OSM): base más sólida. Combinaciones: solo OSM 99 · solo Google 98 · Google+OSM 53 · solo AGC 11. Aparecer en más de una fuente aumenta la confianza, pero no reemplaza la validación.

## 9. ¿Qué queda pendiente?

- 42 casos en revisión manual; validación territorial; posibles locales cerrados/faltantes. 11 cadenas auditadas sin alertas; falsas fusiones: 0.

## Casos emblemáticos (a validar documentalmente)

- **LA JUVENIL** — fundada el 1 de diciembre de 1959 (Colegiales); negocio familiar de tres generaciones. Fuentes: La Nación, El Cronista (caso documentado).
- Raviolón (1971, secundaria) y Master Pastas (1995) a confirmar; Biasatti reciente (2020). Multipasta, Pastas Mazzeo y Caprizzi sin año verificable. Detalle en `fuentes_historicas_casas_pastas.csv`. No se infiere antigüedad por fama.

## 10. ¿Qué aporta a DataGastro?

Un método replicable (registro oficial + fuentes abiertas + señal operativa + auditoría de calidad) para otros rubros: pizzerías, heladerías artesanales, cafeterías de especialidad, panaderías, parrillas, casas de empanadas.

## Limitaciones

- No es censo definitivo ni padrón oficial. Google/OSM no son oficiales. AGC es oficial pero angosto y no implica local activo. Puede haber locales cerrados o faltantes. La deduplicación es heurística. Falta validación manual/campo.
