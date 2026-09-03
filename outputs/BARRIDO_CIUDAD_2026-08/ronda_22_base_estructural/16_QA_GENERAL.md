# QA general

| control | estado | detalle |
|---|---|---|
| geometrias_validas | PASS | 39/39 |
| geometrias_vacias | PASS | 0 |
| polo_ids_unicos | PASS | 39 |
| establecimiento_ids_unicos | PASS | 225 |
| sistemas_miembros_validos | PASS | 5/5 identidades en criterio_admision_55 |
| chacagiales_villa_ortuzar_relacion | PASS | 732 -> 795; 69/69; relación sin fusión |
| baek_ku_independiente | PASS | sin padre Z39 |
| z54_padre_z40 | PASS | POLO-Z40 |
| bares_notables_canonicos | PASS | 90 |
| referentes_sin_coordenada_identificados | PASS | HITO-MG-0017;HITO-MG-0013;HITO-MG-0004;HITO-MG-0010;HITO-MIC-028 |
| referentes_fuera_ficha_identificados | PASS | 52 |
| conteos_reconciliados | PASS | 10819/11119/300 |
| ninguna_duplicacion_triple | PASS | 2 |
| via_a_nueve_reconciliadas | PASS | 9 |
| comunas_barrios_validos | PASS | comunas=15; barrios=48; residual explícito si corresponde |
| porcentajes_territoriales_cierran | PASS | min=99.999998; max=100.000001 |
| overture_no_prueba_apertura | PASS | 0 estados derivados sólo de Overture |
| requests_api | PASS | 0; el script no importa clientes de red |
| make_valid_r08_r12 | PASS | 2/2 PASS |
| z54_contencion_100_pct | PASS | diferencia <=1 m2 |

## Privacidad y alcance

- Se exportan nombres y domicilios públicos de establecimientos porque son el objeto explícito de la capa; no se exportan contactos, CUIT/DNI, correos, nombres de personas, claves ni vínculos privados.
- Los textos libres de R11 no se copiaron. Las fuentes de verificación se minimizaron y sanitizaron.
- Las cinco filas sin coordenada están identificadas en `02_BASE_CANDIDATA.csv` y no entran en `15_MAP_INPUT_REFERENTES.geojson`.
- QA propio del productor: no reemplaza auditoría independiente.
