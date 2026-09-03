# Handoff - Google Places microzonas ampliacion completa v1

Fecha de corrida: 2026-07-09.
Estado: EXPERIMENTAL / no oficial.

## Comandos ejecutados

```powershell
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/preparar_consultas_places_ampliacion.py --tanda b_consolidacion --execute --confirm-real-api
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/refinar_celdas_saturadas_places.py --cells MZ_CHACARITA_C044,MZ_CHACARITA_C075 --grid 3x3 --max-new-requests 165 --run-id chacarita_saturadas_3x3 --execute --confirm-real-api
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/construir_integracion_completa_v1.py
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/detectar_microzonas_completa_v1.py
```

## Scripts nuevos o modificados

- `scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/preparar_consultas_places_ampliacion.py`
- `scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/construir_integracion_completa_v1.py`
- `scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/detectar_microzonas_completa_v1.py`
- `scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/refinar_celdas_saturadas_places.py`

## Outputs principales

- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/places/places_sanitizado_b_consolidacion.csv`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/places/qa_saturacion_b_consolidacion.json`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/places/refinamientos/plan_refino_chacarita_saturadas_3x3.csv`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/places/refinamientos/places_sanitizado_refino_chacarita_saturadas_3x3.csv`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/UNIVERSO_COMPLETO_SANITIZADO.csv`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/places_nuevos_completo_sanitizado.csv`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/tabla_deduplicacion_resumen.csv`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/MICROCLUSTERS_COMPLETA_V1.geojson`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/POLIGONOS_MICROZONAS_COMPLETA_V1.geojson`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/mapas/`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/qa_integracion_completa_v1.json`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/qa_clusters_completa_v1.json`
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/qa_visual_mapas_completa_v1.json`

## Internos no publicables

Todo lo siguiente queda bajo `interno/`, ignorado por Git:

- resultados internos con `google_place_id_interno`;
- progreso de celdas;
- deduplicacion interna con `place_id`;
- resultados internos de refinamiento.

## Proxima decision recomendada

No gastar el margen restante automaticamente. Antes de refinar Recoleta, Villa Crespo o
Caballito, definir un criterio de priorizacion de celdas saturadas. Refinar las 58 celdas
de Tanda B con 2x2 requiere 232 consultas y supera el margen remanente.

Con la informacion actual ya alcanza para recalcular microclusters y poligonos finales
experimentales. La siguiente etapa deberia ser revision humana/visual de los 11 mapas y
ajuste editorial de nombres/cortes, no mas llamadas API por defecto.
