# Plan de ampliación Google Places — microzonas PolosGastro (v1)

**Fecha:** 2026-07-09 · **Estado: DRY-RUN — ninguna llamada ejecutada.** EXPERIMENTAL,
no oficial. Requiere autorización explícita de Diego POR TANDA antes de ejecutar.

## Cobertura: qué está hecho y qué falta

| Estado | Macrozonas (contenedoras) |
|---|---|
| **Escaneadas (piloto 2026-07-09)** | Palermo Soho, Palermo Hollywood, Av. Corrientes, Microcentro y Centro, Belgrano, San Telmo — 379 consultas, cobertura completa. **No se reescanean** (la foto es del mismo día; reescaneo solo por refresco temporal o refinamiento de celdas saturadas, no ahora). |
| **Pendientes (esta ampliación)** | Chacarita, Villa Crespo, Puerto Madero, Recoleta, Caballito, Costanera Norte, Av. Caseros/Barracas — 1.726 ha. |

Palermo (zona completa) no es contenedor de clustering y no se consulta. Los objetivos
tipo Fitz Roy / Plaza Serrano / Barrio Chino / Defensa ya están escaneados: su mejora
pendiente es editorial (cortes), no de datos.

## Estrategia

1. **Dos tandas bajo el mismo hard cap (450/corrida) y con autorización propia:**
   - **Tanda A — críticas (recomendada primero):** Chacarita, Puerto Madero, Costanera
     Norte, Caseros/Barracas. Son las zonas donde F01+F02 es más débil (Costanera: 5
     puntos; Caseros: 18; Puerto Madero: 85 en 503 ha) y donde la revisión de macrozonas
     dejó dos casos "no aprobar todavía por falta de evidencia" — Places puede zanjar si
     hay oferta real no registrada.
   - **Tanda B — consolidación:** Recoleta, Villa Crespo, Caballito (F01+F02 razonable;
     Places densifica y valida, como hizo en San Telmo).
2. **Contención estricta** (igual que el piloto corregido): los puntos fuera de la
   macrozona se descartan al construir el universo.
3. **Sin duplicación:** dedup por `place_id` interno dentro de la corrida; al armar el
   universo ampliado, dedup adicional por `place_id` contra el interno del piloto (los
   bordes Chacarita×Hollywood se tocan) y las reglas 15 m / 40 m + nombre contra F01+F02.
4. **Registro de saturación (novedad):** celdas que devuelven 20/20 quedan en
   `qa_saturacion_<tanda>.json` → una tanda futura de refinamiento puede re-escanear con
   grilla fina SOLO esas celdas, en vez de densificar todo a ciegas.

## Parámetros (comparados con el piloto)

| Parámetro | Piloto | Ampliación | Decisión |
|---|---|---|---|
| Grilla / radio / borde | 180 m / 135 m / 40 m | igual | Mantener: validados (379 consultas, 0 errores) y comparables |
| includedTypes / FieldMask / filtros | gastro + operativo | iguales | Mantener |
| Cap por corrida | 450 | 450 | Mantener; por eso 2 tandas |
| Grilla fina en zonas densas | no | **diferida** | Las 7 pendientes son menos densas que Soho/Corrientes; refinar después solo celdas saturadas |
| Dedup posterior | place_id + 15/40 m | igual + cruce con interno del piloto | Bordes entre macrozonas |

## Dry-run (2026-07-09) — presupuesto

| Tanda | Zona | Celdas (= consultas) |
|---|---|---|
| A críticas | Puerto Madero | 176 |
| A críticas | Chacarita | 93 |
| A críticas | Costanera Norte | 59 |
| A críticas | Caseros/Barracas | 23 |
| **A subtotal** | | **351 — ≤ USD 12,29** |
| B consolidación | Caballito | 121 |
| B consolidación | Recoleta | 83 |
| B consolidación | Villa Crespo | 56 |
| **B subtotal** | | **260 — ≤ USD 9,10** |
| **TOTAL** | | **611 — ≤ USD 21,39** |

Advertencias de presupuesto:
- Costo unitario SKU Enterprise (incluye rating): USD 35/1.000. La cuota gratuita
  mensual (~1.000 llamadas Enterprise) ya absorbió 379 del piloto este mes: si se corre
  todo en julio, ~0–100 consultas podrían quedar gratis; presupuestar el total.
- **Zona más cara:** Puerto Madero (176 consultas, USD 6,16) — es también la de menor
  densidad esperada (85 F01 en 503 ha); si se quiere recortar gasto, es el mejor
  candidato a acotar (p. ej. franja este de los diques) ANTES de ejecutar.
- **Zonas más críticas metodológicamente:** Costanera Norte y Caseros/Barracas — el
  resultado puede cambiar su estado editorial ("no aprobar todavía") en cualquier
  dirección; documentar el veredicto en la revisión de macrozonas.

## Outputs previstos (todo en `google_places_microzonas_ampliacion_v1/`, base del piloto intacta)

- `places/plan_consultas_<tanda>.csv` (ya generados) · `places/places_sanitizado_<tanda>.csv`
  (sin place_id) · `places/qa_saturacion_<tanda>.json`.
- `interno/` (place_id + técnicos; **ya agregado a .gitignore**).
- Tras ejecutar, adaptando las etapas 2–5 del piloto: `UNIVERSO_AMPLIADO_SANITIZADO.csv`
  (con tabla de deduplicación), `MICROCLUSTERS_AMPLIACION.geojson`,
  `POLIGONOS_MICROZONAS_AMPLIACION.geojson`, mapas PNG por macrozona con QA visual,
  QA de privacidad, informe corto de resultados y handoff.

## Comandos de ejecución (SOLO con autorización explícita)

```
# Tanda A (críticas, 351 consultas, <= USD 12,29):
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/preparar_consultas_places_ampliacion.py --tanda a_criticas --execute --confirm-real-api

# Tanda B (consolidación, 260 consultas, <= USD 9,10):
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/preparar_consultas_places_ampliacion.py --tanda b_consolidacion --execute --confirm-real-api
```

Dry-run (sin key, sin costo, re-imprime este presupuesto):
```
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/preparar_consultas_places_ampliacion.py
```

## Recomendación

**Ejecutar por tandas, A primero.** La tanda A resuelve las zonas con evidencia débil
(máximo valor de decisión por dólar); con sus resultados se puede recalibrar B (p. ej.
si Puerto Madero devuelve poco, acotar Caballito/Recoleta no hace falta — son densas).
Correr todo junto (611) también es viable en dos corridas seguidas, pero no aporta nada
frente a escalonar y pierde la chance de ajustar entre tandas.
