# HANDOFF — Prototipo V1 de microzonas + Validación (2026-07-08)

## Qué se pidió (dos tandas el mismo día)

**Tanda A (diseño→prototipo):** construir evidencia (7 etapas) para validar si el pipeline
de microzonas definitivo (diseñado antes) produce mejores resultados que las tandas DBSCAN
anteriores. **Tanda B (validación con casos reales):** dejar de agregar funcionalidades y
validar visual + editorialmente si los microclusters representan la realidad gastronómica
porteña, con segunda pasada jerárquica sobre clusters gigantes y tipología de polos.
Restricciones ambas tandas: todo en `*/experimentos/`, sin commits, sin tocar Fase 25 ni
mapas oficiales, sin Google Places como fuente.

## Qué se hizo — Tanda A (prototipo V1, 7 etapas)

Scripts `scripts/polos_gastro/experimentos/pipeline_microzonas_v1/config.py` + `s01`…`s05`.
Universo V1 = 9.739 entidades (F01+F02, dedup espacial+textual); 4.615 asignadas a 12
macrozonas (contenedor = hull de semilla + buffer 500 m); HDBSCAN por macrozona = 83
clusters (11 macrozonas; Costanera Norte sin evidencia suficiente); 419 polígonos por 6
métodos; 502 filas de métricas objetivas. Docs: `REGLAS_UNIVERSO_V1.md`,
`COMPARACION_DBSCAN_HDBSCAN_HIBRIDO.md`, `INFORME_FINAL_PROTOTIPO_V1.md`. Detalle completo
de números en `INFORME_FINAL_PROTOTIPO_V1.md`.

## Qué se hizo — Tanda B (validación, 7 etapas), en `.../pipeline_microzonas_v1/validacion/`

Scripts nuevos: `s06_validacion_visual.py` (tableros), `s07_segunda_pasada.py` (jerárquico),
`s08_tipologia_polos.py` (clasificación automática).

1. **8 casos de estudio** (`CASOS_DE_ESTUDIO.md`): Palermo, Avenida Corrientes, San Telmo,
   Belgrano, Chacarita, Villa Crespo, Avenida Caseros/Barracas, Costanera Norte — cubren
   multi-núcleo, corredor, dominante+satélites, problema histórico (Chacarita), evidencia
   insuficiente y baja confianza.
2. **Tableros visuales** (`outputs/.../validacion/tableros/`): un mapa rico por macrozona
   con callejero GCBA, subzonas editoriales de referencia (fase16, donde existen), clusters,
   polígonos híbridos y nombres de locales relevantes.
3. **Diagnóstico editorial** (`DIAGNOSTICO_EDITORIAL_CASOS.md`): interpretación caso por
   caso, no solo métricas.
4. **Segunda pasada jerárquica** (`SEGUNDA_PASADA_MACROZONAS_GRANDES.md` +
   `outputs/.../segunda_pasada/`): los 6 clusters > 35 ha se re-clusterizan con HDBSCAN
   leaf/epsilon=25m. Funciona muy bien en compactos (Microcentro, Palermo: 10-11 focos
   útiles); poda en alargados (Belgrano: 61 % ruido) — hallazgo clave para V2.
5. **Tipología automática** (`TIPOLOGIA_POLOS.md`): 5 categorías emergentes (7 multi-núcleo,
   2 dominante+satélites, 1 disperso, 1 evidencia insuficiente, 1 baja confianza).
6. **Informe de validación metodológica** (`INFORME_VALIDACION_METODOLOGICA.md`) — **el
   documento central**: responde la pregunta de Diego (¿un experto en gastronomía porteña
   avalaría estos microclusters?). **Respuesta: sí, salvo casos puntuales**, con causa
   raíz identificada (el contenedor de macrozona derivado de semilla, no la técnica de
   clustering).
7. **Recomendación V2** (`RECOMENDACION_PIPELINE_V2.md`, sin implementar): (1) contornos
   editoriales reales de los 12 polos — prioridad máxima; (2) segunda pasada condicionada
   a forma del cluster (no un epsilon único); (3) tratamiento diferenciado por tipología;
   explícitamente NO cambiar el detector HDBSCAN ni incorporar Places todavía.

## Hallazgos que trascienden el experimento

- Editorial "Corrientes 9 de Julio-Callao" (elipse fase16) queda vacía de clusters; el
  cluster grande real cae en San Nicolás — desajuste sin resolver sin trabajo de campo.
- San Telmo tiene 2 clusters (C4 norte, C1 sur) fuera de toda elipse editorial — mismo
  síntoma: contenedor de macrozona demasiado ancho.
- Ningún caso mostró fusión de identidades editoriales distintas en un cluster
  irreconocible; el error dominante es "cluster fuera de la zona esperada" o "núcleo que
  debería subdividirse", ambos con causa en el contenedor, no en HDBSCAN.

## Pendiente (orden recomendado, detalle en RECOMENDACION_PIPELINE_V2.md)

(1) Digitalizar los 12 contornos editoriales · (2) re-correr Etapas 3-5 con contornos
nuevos y repetir validación visual · (3) segunda pasada condicionada a forma ·
(4) recién entonces, corrida completa versionada (Fase D). Sin commits: todo el árbol
sigue untracked.
