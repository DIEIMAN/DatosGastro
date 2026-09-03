# Prompt para Claude Code — auditoría independiente de San Telmo

## Objetivo

Auditar de forma independiente la ampliación sucesora de San Telmo que incorpora la manzana del Mercado, sin corregirla ni regenerarla.

## Inputs canónicos

- `AGENTS.md` y reglas DataGastro aplicables.
- Baseline, sólo lectura: `outputs/BARRIDO_CIUDAD_2026-08/ronda_22_correccion_relaciones_2026-08-12/`.
- Producción a auditar: `outputs/BARRIDO_CIUDAD_2026-08/ronda_22_sucesora_san_telmo_2026-08-12/`.
- Script productor, sólo lectura: `outputs/BARRIDO_CIUDAD_2026-08/ronda_22_sucesora_san_telmo_2026-08-12/scripts/build_san_telmo.py`.
- Capas de contraste locales: `outputs/BARRIDO_CIUDAD_2026-08/insumos_ciudad/manzanas.geojson`, `outputs/BARRIDO_CIUDAD_2026-08/insumos/caba_barrios.geojson` y `outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/BASE_GASTRONOMICA_estado_2026-08-12.csv`.

## Acciones

1. Verificar los hashes y manifiesto de la sucesora.
2. Recalcular desde cero, sin reutilizar las variables del script productor: validez en EPSG:4326 y 5347, inclusión del mercado, área previa/posterior, locales previos/posteriores, solapes con los otros 38 polos y distribución por barrio.
3. Confirmar que la manzana usada es `id=7783`, `sm=004 - 029`, y que la tolerancia de 1 m sólo corrige la diferencia instrumental del punto respecto de la manzana.
4. Verificar las 190 relaciones: 139 interiores, 51 exteriores, Mercado de San Telmo interior próximo al borde y 17 dudosas sin cambio.
5. Confirmar que `ICONOS_PRINCIPALES_PROPUESTOS.csv` conserva exactamente 66 filas y es idéntico por hash al baseline.
6. Evaluar si aplicar el delta +16 al baseline canónico —10.819/11.119/300— está correctamente documentado frente a la discrepancia de una unidad de la librería local.
7. Escribir sólo en `outputs/AUDITORIA_INDEPENDIENTE_SAN_TELMO_SUCESORA_2026-08-12/`: `INFORME.md`, `QA_RECALCULO.json`, cualquier script reproducible y `MANIFEST.csv` con SHA-256.

## Prohibiciones

- No modificar baseline, sucesora, Atlas, geometrías, relaciones, íconos ni fuentes.
- No investigar las 52 relaciones documentales: esa tarea pertenece a Cowork.
- No usar APIs, web, Drive, credenciales, datos privados ni scraping.
- No hacer commit, push, staging ni borrar archivos.
- No aprobar institucionalmente la sucesora: emitir `APROBABLE`, `REQUIERE_CORRECCION` o `BLOQUEADA` con fundamento verificable.

## Criterio de aceptación

La auditoría termina cuando todos los cálculos están reproducidos independientemente, los conteos y hashes se informan, cualquier divergencia se distingue entre material e instrumental, los 66 íconos se confirman intactos y el dictamen queda escrito únicamente en la carpeta nueva con manifiesto válido. Si se detecta una divergencia material, no corregir: detener la aprobación y documentar el caso exacto.
