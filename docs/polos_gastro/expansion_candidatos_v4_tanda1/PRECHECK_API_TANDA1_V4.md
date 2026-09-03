# Precheck API — Tanda 1 Expansión V4

**Estado:** `REUSE_ONLY`  
**Carácter:** EXPERIMENTAL / NO OFICIAL  
**Fecha de corte:** 2026-07-12

## Resultado

- Plan Tanda 1: 1020 filas categoría×celda.
- Reutilizar existente: 645.
- Consultar solo brecha: 330.
- Pendiente de decisión, excluidas: 45.
- Celdas físicas nuevas: 66 (cinco categorías por celda).
- Credencial: GOOGLE_MAPS_API_KEY=AUSENTE, GOOGLE_PLACES_API_KEY=AUSENTE.

No se leyó `.env` y no se expuso ningún secreto. No se habilita la API; corresponde completar en modo de reutilización.

## Controles

| Control | Estado | Detalle |
|---|---|---|
| zonas | OK | reales=['Z01', 'Z02', 'Z03', 'Z04']; esperadas=['Z01', 'Z02', 'Z03', 'Z04'] |
| conteo_REUTILIZAR_EXISTENTE | OK | real=645; esperado=645 |
| conteo_CONSULTAR_SOLO_BRECHA | OK | real=330; esperado=330 |
| conteo_PENDIENTE_DECISION | OK | real=45; esperado=45 |
| conteo_Z01_REUTILIZAR_EXISTENTE | OK | real=95; esperado=95 |
| conteo_Z01_CONSULTAR_SOLO_BRECHA | OK | real=105; esperado=105 |
| conteo_Z01_PENDIENTE_DECISION | OK | real=0; esperado=0 |
| conteo_Z02_REUTILIZAR_EXISTENTE | OK | real=340; esperado=340 |
| conteo_Z02_CONSULTAR_SOLO_BRECHA | OK | real=45; esperado=45 |
| conteo_Z02_PENDIENTE_DECISION | OK | real=0; esperado=0 |
| conteo_Z03_REUTILIZAR_EXISTENTE | OK | real=170; esperado=170 |
| conteo_Z03_CONSULTAR_SOLO_BRECHA | OK | real=175; esperado=175 |
| conteo_Z03_PENDIENTE_DECISION | OK | real=45; esperado=45 |
| conteo_Z04_REUTILIZAR_EXISTENTE | OK | real=40; esperado=40 |
| conteo_Z04_CONSULTAR_SOLO_BRECHA | OK | real=5; esperado=5 |
| conteo_Z04_PENDIENTE_DECISION | OK | real=0; esperado=0 |
| categorias | OK | reales=['bakery', 'bar', 'cafe', 'meal_takeaway', 'restaurant'] |
| radio | OK | valores=[200.0] |
| coordenadas_numericas | OK | nulos=0 |
| coordenadas_caba | OK | bbox prudencial CABA |
| ids_unicos | OK | duplicados=0 |
| pendientes_excluidas | OK | pendientes=45; autorizadas=975 |
| dentro_areas_autorizadas | OK | validación contra subunidad explícita o área principal; fuera=0 |
| brechas_no_en_cache | OK | centros_brecha=66; coincidencias_centro=0 |
| flag_equivalencia_brechas | OK | filas_con_equivalente=0 |
| staging_vacio | OK | archivos_staged=0 |
| credencial_entorno | ERROR | GOOGLE_MAPS_API_KEY=AUSENTE; GOOGLE_PLACES_API_KEY=AUSENTE |
