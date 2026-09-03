# Contrato de universo de puntos — Expansión V4

**Fecha:** 2026-07-12

## Universo base reutilizable

`outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/UNIVERSO_COMPLETO_SANITIZADO.csv`

- 6.461 puntos (3.240 F01+F02; 3.221 Google Places)
- Fecha Places: 2026-07-08/09

## Campos mínimos del universo de expansión (futuro)

| Campo | Descripción |
|---|---|
| point_id_sanitizado | ID sin PII |
| fuente | F01+F02 / google_places / mixto |
| fuente_original | detalle de origen |
| categoría_normalizada | rubro |
| lat, lon | WGS84 |
| fecha_fuente | corte |
| zona_consulta | zona_id de la ventana |
| subunidad_consulta | subunidad_id |
| coincidencia_f01_f02 | flag match |
| coincidencia_places | flag match |
| dedup_cluster_id | grupo dedup |
| qa_status | OK/REVISAR/EXCLUIDO |
| exclusion_reason | si aplica |
| publicable | SI/NO |

## Privacidad

- No exportar nombres comerciales a paquetes de revisión pública.
- Caches internos (`places_consolidados_interno.csv`) solo lectura interna.
- Nunca commitear place_id + teléfono + address completa.

## Deduplicación

Reutilizar reglas de `construir_integracion_completa_v1.py` (place_id, distancia+nombre, match F01/F02).
