# Contrato de consulta Places — Expansión V4

**Fecha:** 2026-07-12  
**Estado:** preflight — **no ejecutar sin autorización humana**

## Principios

1. Reutilizar resultados 2026-07-08/09 antes de consultar.
2. No repetir celda+categoría ya cubierta.
3. Solo brechas territoriales o categoriales.
4. No inventar tipos de lugar fuera del pipeline vigente.
5. Control de saturación (refino 3×3 si tope de resultados).

## Categorías

### Primarias (consulta planificada)
- `restaurant`
- `cafe`
- `bar`
- `bakery`
- `meal_takeaway`

### Auxiliares (solo si brecha justificada)
- `meal_delivery`
- `food`

### Excluidas
- `lodging`
- `store`
- `shopping_mall`

## Parámetros de grilla

| Parámetro | Valor |
|---|---|
| CRS métrico | EPSG:5347 |
| celda_m | 250 |
| radio_m | 200 |
| borde_m | 150 |

## Campos mínimos de plan

`consulta_id, tanda, zona_id, subunidad_id, celda_id, lat, lon, radio_m, categoría, estado, reutilizar, motivo_consulta`

## Estados de fila

- `REUTILIZAR_EXISTENTE`
- `CONSULTAR`
- `CONSULTAR_SOLO_BRECHA`
- `NO_CONSULTAR`
- `PENDIENTE_DECISION`

## Prohibiciones

- No consultar C-S02 (Bajo porteño ambiguo) hasta definición.
- No usar lista semilla de locales como query de validación de polo.
- No guardar place_id/nombres en paquetes públicos.

## Scripts plantilla (solo lectura / copiar)

- `scripts/polos_gastro/experimentos/google_places_microzonas_piloto/preparar_consultas_places_piloto.py`
- `scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/preparar_consultas_places_ampliacion.py`
- `scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/refinar_celdas_saturadas_places.py`
