# Infraestructura cartográfica v1 de PolosGastro — índice

**Fecha:** 2026-07-08 · **Carácter:** experimental, paralelo. No toca Fase 25 ni mapas
oficiales; no hay commits.

Documentos (en orden de lectura):

1. [`01_INVENTARIO_REFERENCIAS_CARTOGRAFICAS.md`](01_INVENTARIO_REFERENCIAS_CARTOGRAFICAS.md)
   — qué existe hoy (callejero GCBA, fichas de polo, elipses de fase16, PDF semilla) y qué
   no existe (ningún polígono real de macrozona, ni siquiera en el informe oficial vigente).
2. [`02_DISENO_CAPA_EDITORIAL.md`](02_DISENO_CAPA_EDITORIAL.md) — esquema de
   `macrozonas_editorial_vN.geojson` (16 atributos, jerarquía polo/subzona).
3. [`03_HERRAMIENTA_EDICION.md`](03_HERRAMIENTA_EDICION.md) — QGIS/geojson.io como
   editor recomendado + kit de capas de referencia por macrozona (`preparar_kit_edicion.py`).
4. [`04_INTEGRACION_EXPERIMENTAL_PALERMO_SOHO.md`](04_INTEGRACION_EXPERIMENTAL_PALERMO_SOHO.md)
   — caso real: contorno trazado sobre el callejero, comparado contra el pipeline actual.
5. [`05_VERSIONADO.md`](05_VERSIONADO.md) — snapshots inmutables, CHANGELOG, diff automático.
6. [`06_QA_CAPA_EDITORIAL.md`](06_QA_CAPA_EDITORIAL.md) — gates duros + banderas, probado
   contra datos reales.
7. [`07_ROADMAP_DEFINITIVO_POLOSGASTRO.md`](07_ROADMAP_DEFINITIVO_POLOSGASTRO.md) —
   síntesis: infraestructura permanente / proceso operativo / desarrollo futuro.

Scripts en `scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/`:
`preparar_kit_edicion.py`, `construir_poligono_real_palermo_soho.py`,
`normalizar_capa_editorial.py`, `simular_pipeline_editorial_palermo_soho.py`,
`comparar_versiones_editorial.py`, `qa_capa_editorial.py`.

Salidas en `outputs/polos_gastro/experimentos/infraestructura_cartografica_v1/`.

## Tanda 2 (2026-07-08, noche) — `macrozonas_v1_experimental` (primera versión operativa)

8. [`METODOLOGIA_MACROZONAS_V1.md`](METODOLOGIA_MACROZONAS_V1.md) — ficha por macrozona
   (14 features: 12 polos + Soho/Hollywood): método, fuente, dudas, qué revisar.
9. [`QA_MACROZONAS_V1.md`](QA_MACROZONAS_V1.md) — gates/banderas + contención de
   entidades; encontró y resolvió una geometría inválida real (Caballito) y un
   solapamiento operativo serio (Corrientes/Microcentro, 406 entidades).
10. [`COMPARACION_CONTENEDORES_ANTERIORES_VS_MACROZONAS_V1.md`](COMPARACION_CONTENEDORES_ANTERIORES_VS_MACROZONAS_V1.md)
    — prueba de pipeline en Palermo Soho/Hollywood y Avenida Corrientes.
11. [`HANDOFF_MACROZONAS_V1_2026_07_08.md`](HANDOFF_MACROZONAS_V1_2026_07_08.md).

Scripts nuevos: `construir_macrozonas_v1.py`, `qa_macrozonas_v1.py`,
`generar_mapas_macrozonas_v1.py`, `probar_pipeline_macrozonas_v1.py`. Capa resultante:
`outputs/.../macrozonas_v1_experimental.geojson` (14 features) + mapas
(`mapa_general_macrozonas_v1.png`, `mapa_entidades_macrozonas_v1.png`,
`mapa_confianza_macrozonas_v1.png`, `mapas_individuales/`).

## Tanda 3 (2026-07-08, noche) — calibración y `macrozonas_editoriales_candidatas_v1`

12. [`FICHAS_TECNICAS_MACROZONAS_V1.md`](FICHAS_TECNICAS_MACROZONAS_V1.md) — ficha de
    revisión de las 12 macrozonas (nombre, confianza, superficie, entidades, barrios,
    calles límite, fuente, problemas, observaciones) antes de corregir nada.
13. [`CORRECCIONES_BLOQUEANTES_ANTES_DESPUES.md`](CORRECCIONES_BLOQUEANTES_ANTES_DESPUES.md)
    — los 4 bloqueantes (Corrientes/Microcentro, Belgrano, Costanera Norte, Chacarita):
    antes, después y justificación de cada corrección.
14. [`QA_CORRECCIONES_BLOQUEANTES.md`](QA_CORRECCIONES_BLOQUEANTES.md) — QA acotado a las
    macrozonas modificadas: el solapamiento Corrientes/Microcentro queda en 0; Belgrano
    gana 84 entidades pero pierde 53 sin cobertura (a revisar); cobertura total de CABA
    baja de 19,66 % a ~12-19 % según se incluya o no el polo contextual Palermo.
15. [`REVISION_DGDGAS_MACROZONAS_CANDIDATAS_V1.md`](REVISION_DGDGAS_MACROZONAS_CANDIDATAS_V1.md)
    — **documento no técnico** para que el equipo de DGDGAS revise cada macrozona y
    marque ✓ aprobar / △ modificar / ✗ rehacer, con trazabilidad hacia el `id` de cada
    feature.

Scripts nuevos: `corregir_bloqueantes_v1.py`, `qa_correcciones_bloqueantes.py`,
`ensamblar_macrozonas_candidatas_v1.py`. Capa candidata:
`outputs/.../macrozonas_editoriales_candidatas_v1.geojson` (14 features: 4 corregidas +
10 sin cambios) — pasa el QA completo con 0 gates duros. Mapas propios en
`mapa_general_macrozonas_editoriales_candidatas_v1.png`,
`mapa_confianza_macrozonas_editoriales_candidatas_v1.png`,
`mapas_individuales_macrozonas_editoriales_candidatas_v1/`. Confianza: sube de 2 alta/7
media/5 baja a **2 alta/9 media/3 baja**.
