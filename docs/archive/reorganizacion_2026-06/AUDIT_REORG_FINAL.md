# AUDIT_REORG_FINAL — Reporte final de auditoría post-reorganización

**Fecha:** 2026-06-29 · **Rama:** `mercados-gastronomicos-v2`
**Commit/push:** NO se hizo commit ni push. No se usó `git add`. Nada borrado.

---

## 0. Actualización del validador y reauditoría (rev. 2 · 2026-06-29)

Se actualizó `src/mercados_caba/validate_mercados_setup.py` para validar **solo la cadena vigente**
de Mercados (antes exigía 62 archivos históricos hoy en cuarentena). Esto disolvió el principal
motivo de REVIEW_REQUIRED. Tras la actualización:

- ✅ Validador actualizado: **EXIT 0, 56 verificaciones OK, 0 errores** (incluye 14 páginas, footer,
  anclas p7/p11/p14 y ausencia de 'V4_1').
- ✅ Prueba fuerte repetida con `_delete_candidates/` desactivado: Mercados OK, Casas OK,
  DataGastro general OK=62, **y el validador actualizado también pasó**.
- 🔎 Hallazgo técnico: 46 candidatos parecían "referenciados por código vigente", pero la
  inspección mostró que son **menciones en strings/instrucciones** o lecturas en **rutas de código
  no ejecutadas por la cadena del PDF** (p. ej. `main()`/`build_support_files()` de
  `build_pdf_final_v4_1_from_v3.py`, que la cadena `con_horarios` no invoca — sí usa
  `importlib` para llamar solo `build_pdf_v2/v3`, `build_new_pages`, etc.). La prueba fuerte lo confirma.

### Conteos reclasificados

| Categoría | rev.1 | **rev.2** |
|---|---|---|
| SAFE_TO_DELETE_AFTER_APPROVAL | 164 | **224** |
| KEEP_AS_ARCHIVE | 42 | **53** |
| REVIEW_REQUIRED | 82 | **11** |
| DO_NOT_DELETE | 0 | **0** |

Detalle: `AUDIT_DELETE_CANDIDATES.md` (rev.2) y `.csv` (columna `prev_classification` registra el cambio).

---

## 1. Resumen ejecutivo (rev. 1 — preservado)

Se auditaron los **288 archivos** en `_delete_candidates/`. La conclusión central:
**ninguna cadena de generación de entregables vigentes depende de la cuarentena.** Se verificó
regenerando Mercados, Casas de Pastas y validando DataGastro general con la carpeta
`_delete_candidates/` renombrada a `_delete_candidates__DISABLED_AUDIT/` (prueba fuerte): las tres
pasaron. La cuarentena fue restaurada inmediatamente.

Hallazgo principal que evita un borrado a ciegas: el validador de andamiaje
`src/mercados_caba/validate_mercados_setup.py` (que se conservó in situ) declara en sus listas
`EXPECTED_DOCS`/`EXPECTED_CSV` **62 archivos que hoy están en cuarentena** y verifica su
existencia. No son insumos del PDF final (el PDF regenera sin ellos), pero ese validador
reporta **68 errores** tras la reorganización. Por eso esos archivos se marcaron
**REVIEW_REQUIRED**, no SAFE: borrarlos exige decidir antes qué se hace con ese validador.

## 2. Conteos por categoría

| Categoría | Cantidad |
|---|---|
| SAFE_TO_DELETE_AFTER_APPROVAL | 164 |
| KEEP_AS_ARCHIVE | 42 |
| REVIEW_REQUIRED | 82 |
| DO_NOT_DELETE | 0 |
| **TOTAL** | **288** |

## 3. Resultado de las pruebas de cadena vigente

| Prueba | Resultado |
|---|---|
| Mercados regenera (`build_pdf_final_con_horarios.py`) | ✅ EXIT 0 |
| PDF Mercados = 14 páginas | ✅ |
| p7 horarios documentales concretos | ✅ |
| p11 'Activar patios públicos como dinamizadores barriales.' | ✅ |
| p14 'Alcances del relevamiento y próximos pasos para consolidar la base candidata.' | ✅ |
| Footer 'DataGastro · Mercados gastronómicos de CABA · Informe final' | ✅ |
| PDF Mercados NO contiene 'V4_1' | ✅ |
| Casas de Pastas regenera (`build_pdf_integrado_v4.py`) | ✅ EXIT 0, 23 págs |
| DataGastro general (`validate_model.py --strict-real`) | ✅ OK=62, ERROR=0 |
| Prueba fuerte: las 3 cadenas con `_delete_candidates/` DESACTIVADO | ✅ pasaron las 3 |
| `validate_mercados_setup.py` (validador de andamiaje, NO genera entregable) | ⚠️ 68 errores por archivos en cuarentena → ver §5 |

## 4. DataGastro general y V2

- `src/`, `data/`, `sql/`, `dashboard/`, `notebooks/`, `config/`, `schemas/`: intactos (sin cambios trackeados en el core).
- V2 (`config/v2`, `data/v2`, `docs/datagastro_v2`, `outputs/v2`, `schemas/`, `src/v2`): intacto, no mezclado en subproyectos.
- No se movieron crudos ni fuentes sensibles. `.gitignore` protege `_delete_candidates/`, `MercadosGastro/final/`, `CasasDePastas/final/`.
- Pipeline F01–F05: validación `--strict-real` OK=62, ERROR=0.

## 5. Archivos DO_NOT_DELETE

**Ninguno.** La prueba fuerte confirmó que ningún entregable vigente depende de la cuarentena.
Las dependencias detectadas (validador de andamiaje, copias dentro de packs) se clasificaron
como REVIEW_REQUIRED en lugar de DO_NOT_DELETE, porque sus originales/funcionalidad no se pierden
al borrar la copia en cuarentena — pero requieren una decisión explícita antes de borrar.

## 6. Archivos REVIEW_REQUIRED (82) — requieren tu decisión

### 6.a — Esperados por `validate_mercados_setup.py` (66)

Si se borran, ese validador falla. Opciones: (i) actualizar `EXPECTED_DOCS`/`EXPECTED_CSV` para
reflejar la cadena vigente y luego borrar; (ii) conservarlos como archivo histórico del relevamiento.

| Archivo | Tipo | mtime |
|---|---|---|
| `ANEXO_TECNICO_MERCADOS_GASTRONOMICOS_CABA_V3.md` | md | 2026-06-24 16:56 |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V3.md` | md | 2026-06-24 16:55 |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V4.md` | md | 2026-06-24 21:33 |
| `INFORME_MERCADOS_GASTRONOMICOS_CABA_V1_2.md` | md | 2026-06-24 10:07 |
| `INFORME_MERCADOS_GASTRONOMICOS_CABA_V2_2.md` | md | 2026-06-24 15:40 |
| `INFORME_MERCADOS_GASTRONOMICOS_CABA_V2_2.md` | md | 2026-06-24 11:46 |
| `README_REGENERAR_INFORME_V4.md` | md | 2026-06-24 21:33 |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V3.md` | md | 2026-06-24 16:55 |
| `afirmaciones_mercados_v2_3.csv` | csv | 2026-06-24 15:39 |
| `campos_objetivo_mercados.csv` | csv | 2026-06-23 16:14 |
| `candidatos_mercados_fuentes_internas_v2.csv` | csv | 2026-06-24 10:47 |
| `contradicciones_y_brechas_v2_3.csv` | csv | 2026-06-24 15:39 |
| `decisiones_que_permite_tomar_v4.csv` | csv | 2026-06-24 20:52 |
| `fuentes_documentales_mercados_v2.csv` | csv | 2026-06-24 10:15 |
| `fuentes_documentales_mercados_v2_2.csv` | csv | 2026-06-24 11:44 |
| `fuentes_documentales_mercados_v2_3.csv` | csv | 2026-06-24 15:39 |
| `fuentes_internas_mercados_resumen_v2.csv` | csv | 2026-06-24 10:47 |
| `fuentes_mercados_candidatas.csv` | csv | 2026-06-23 16:15 |
| `fuentes_mercados_urls_v0.csv` | csv | 2026-06-23 17:53 |
| `fuentes_mercados_urls_v1.csv` | csv | 2026-06-23 18:15 |
| `fuentes_mercados_urls_v1_2.csv` | csv | 2026-06-23 18:37 |
| `fuentes_url_truncadas_requieren_verificacion_v2_3.csv` | csv | 2026-06-24 15:39 |
| `google_places_matches_v1_2.csv` | csv | 2026-06-24 10:51 |
| `google_places_mercados_resumen_v2.csv` | csv | 2026-06-24 10:51 |
| `google_places_posibles_omitidos_v2.csv` | csv | 2026-06-24 10:51 |
| `indicadores_mercados_gastronomicos_v3.csv` | csv | 2026-06-24 16:53 |
| `mercados_candidatos_iniciales.csv` | csv | 2026-06-23 16:14 |
| `mercados_fuera_alcance_v0.csv` | csv | 2026-06-23 17:53 |
| `mercados_gastronomicos_activos_v1.csv` | csv | 2026-06-23 18:14 |
| `mercados_gastronomicos_activos_v1_2.csv` | csv | 2026-06-23 18:36 |
| `mercados_gastronomicos_activos_v2.csv` | csv | 2026-06-24 10:53 |
| `mercados_gastronomicos_activos_v2_2.csv` | csv | 2026-06-24 11:43 |
| `mercados_gastronomicos_activos_v2_2.csv` | csv | 2026-06-24 11:43 |
| `mercados_gastronomicos_activos_v2_4.csv` | csv | 2026-06-24 16:37 |
| `mercados_gastronomicos_activos_v3.csv` | csv | 2026-06-24 16:52 |
| `mercados_gastronomicos_candidatos_v0.csv` | csv | 2026-06-23 17:52 |
| `mercados_gastronomicos_candidatos_v1.csv` | csv | 2026-06-23 18:13 |
| `mercados_gastronomicos_candidatos_v1_2.csv` | csv | 2026-06-23 18:36 |
| `mercados_gastronomicos_candidatos_v2.csv` | csv | 2026-06-24 10:53 |
| `mercados_gastronomicos_candidatos_v2_2.csv` | csv | 2026-06-24 11:43 |
| `mercados_gastronomicos_cerrados_o_no_activos_v1.csv` | csv | 2026-06-23 18:14 |
| `mercados_gastronomicos_en_revision_v2_2.csv` | csv | 2026-06-24 11:43 |
| `mercados_gastronomicos_en_revision_v2_2.csv` | csv | 2026-06-24 11:43 |
| `mercados_gastronomicos_no_activos_v3.csv` | csv | 2026-06-24 16:52 |
| `mercados_gastronomicos_no_activos_v4.csv` | csv | 2026-06-24 20:52 |
| `mercados_gastronomicos_no_contabilizados_v1_2.csv` | csv | 2026-06-23 18:36 |
| `mercados_gastronomicos_no_contabilizados_v2.csv` | csv | 2026-06-24 10:16 |
| `mercados_gastronomicos_no_contabilizados_v2_2.csv` | csv | 2026-06-24 11:43 |
| `mercados_gastronomicos_pendientes_v1.csv` | csv | 2026-06-23 18:24 |
| `mercados_gastronomicos_pendientes_v1_2.csv` | csv | 2026-06-23 18:36 |
| `mercados_gastronomicos_posibles_omitidos_v2.csv` | csv | 2026-06-24 10:55 |
| `mercados_gastronomicos_posibles_omitidos_v2_2.csv` | csv | 2026-06-24 11:43 |
| `mercados_pendientes_revision_v0.csv` | csv | 2026-06-23 18:25 |
| `oportunidades_politica_publica_mercados_v3.csv` | csv | 2026-06-24 16:53 |
| `publicos_objetivo_mercados_v3.csv` | csv | 2026-06-24 16:53 |
| `referencias_documentales_visibles_v4.csv` | csv | 2026-06-24 20:53 |
| `resumen_relevamiento_mercados_v0.csv` | csv | 2026-06-23 17:54 |
| `resumen_relevamiento_mercados_v1.csv` | csv | 2026-06-23 18:15 |
| `resumen_relevamiento_mercados_v1_2.csv` | csv | 2026-06-23 18:37 |
| `resumen_relevamiento_mercados_v2.csv` | csv | 2026-06-24 10:54 |
| `resumen_relevamiento_mercados_v2_2.csv` | csv | 2026-06-24 11:44 |
| `resumen_relevamiento_mercados_v2_2.csv` | csv | 2026-06-24 11:44 |
| `resumen_relevamiento_mercados_v2_4.csv` | csv | 2026-06-24 16:38 |
| `resumen_relevamiento_mercados_v3.csv` | csv | 2026-06-24 16:53 |
| `taxonomia_mercados.csv` | csv | 2026-06-23 16:14 |
| `validacion_gourmand_food_hall_v2_4.csv` | csv | 2026-06-24 16:37 |

### 6.b — CSV intermedios no esperados por el validador (16)

Sin referencia funcional detectada, pero conviene confirmar que ningún análisis los reutilice.

| Archivo | mtime |
|---|---|
| `README_MERCADOS_DOCUMENTAL_V2_1.md` | 2026-06-24 11:41 |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_V2_2.md` | 2026-06-24 15:33 |
| `afirmaciones_mercados_v2_1.csv` | 2026-06-24 11:41 |
| `contradicciones_y_brechas_v2_1.csv` | 2026-06-24 11:41 |
| `fuentes_documentales_mercados_v2_1.csv` | 2026-06-24 11:41 |
| `horarios_documentados_mercados_vfinal_v2.csv` | 2026-06-26 15:03 |
| `oportunidades_gestion_mercados_v4.csv` | 2026-06-26 10:49 |
| `pilotos_recomendados_mercados_v4.csv` | 2026-06-26 10:49 |
| `posibles_omitidos_documentales_v2_1.csv` | 2026-06-24 11:41 |
| `publicos_objetivo_mercados_vfinal.csv` | 2026-06-25 23:31 |
| `resumen_narrativo_documental_v2_1.md` | 2026-06-24 11:41 |
| `tabla_estado_y_no_contabilizados.csv` | 2026-06-24 10:08 |
| `tabla_por_barrio_comuna.csv` | 2026-06-24 10:08 |
| `tabla_por_gestion.csv` | 2026-06-24 10:08 |
| `tabla_por_tipo.csv` | 2026-06-24 10:08 |
| `tabla_universo.csv` | 2026-06-24 10:08 |

## 7. Ambigüedades declaradas (A/B/C)

**A. `docs/mercados_caba/RESUMEN_EJECUTIVO_..._V4.md`** — está IN SITU (no en cuarentena).
Referenciado por `validate_mercados_setup.py` (EXPECTED_DOCS V4). **Clasificación: KEEP/REVIEW —
conservado.** No borrar sin actualizar el validador.

**B. `docs/datagastro_v2.zip`** — NO tocado. Contiene 11 archivos; la carpeta `docs/datagastro_v2/`
tiene 19. **No es duplicado exacto.** V2 es intocable. **Clasificación: REVIEW_REQUIRED — no borrar.**

**C. Packs de revisión externa** — V4 (`PACK_REVISION_EXTERNA_254_V4`) IN SITU; V3 en cuarentena
(`KEEP_AS_ARCHIVE`). El pack V3 no está referenciado por código vigente; sus CSV internos tienen
equivalentes vivos en `outputs/casas_pastas_integrado/`. **Conservar V3 como snapshot histórico.**

## 8. Confirmaciones finales

- ✅ **Nada borrado** (288 archivos intactos en `_delete_candidates/`).
- ✅ Prueba con cuarentena desactivada: **pasó** para Mercados, Casas y DataGastro general.
- ✅ Mercados regeneró OK (14 págs, checks de contenido OK, sin 'V4_1').
- ✅ Casas de Pastas regeneró OK (23 págs).
- ✅ DataGastro general y V2 intactos; no se rompió el pipeline F01–F05.
- ✅ **Sin commit. Sin push. Sin `git add`.**

## 9. Recomendación operativa

1. Borrar tras tu aprobación los **164 SAFE_TO_DELETE_AFTER_APPROVAL** (PNG/zip/pdf/html y generadores legacy).
2. Mover los **42 KEEP_AS_ARCHIVE** a `MercadosGastro/archive_review/` y `CasasDePastas/archive_review/` (hoy vacías).
3. Decidir sobre los **82 REVIEW_REQUIRED**: principalmente, qué se hace con `validate_mercados_setup.py`.

---

## 10. Listas de la reauditoría (rev. 2)

### 10.a — REVIEW_REQUIRED restantes (11)

Únicos casos con referencia en código vigente (fuera de la cadena del PDF final). Conservar
hasta confirmar que no se correrán esos builders/scripts en modo standalone.

| Archivo | Referencia en código vigente |
|---|---|
| `candidatos_mercados_fuentes_internas_v2.csv` | src\mercados_caba\build_inventario_fuentes_internas_mercados.py |
| `decisiones_que_permite_tomar_v4.csv` | src\mercados_caba\build_pdf_from_markdown_master.py |
| `fuentes_internas_mercados_resumen_v2.csv` | src\mercados_caba\build_inventario_fuentes_internas_mercados.py |
| `google_places_matches_v1_2.csv` | src\mercados_caba\google_places_mercados_enrichment.py |
| `google_places_mercados_resumen_v2.csv` | src\mercados_caba\google_places_mercados_enrichment.py |
| `google_places_posibles_omitidos_v2.csv` | src\mercados_caba\google_places_mercados_enrichment.py |
| `mercados_gastronomicos_no_activos_v4.csv` | src\mercados_caba\build_pdf_from_markdown_master.py |
| `oportunidades_gestion_mercados_v4.csv` | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `pilotos_recomendados_mercados_v4.csv` | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `publicos_objetivo_mercados_vfinal.csv` | src\mercados_caba\build_pdf_final_v4_1_from_v3.py; src\mercados_caba\build_pdf_from_markdown_master.py |
| `referencias_documentales_visibles_v4.csv` | src\mercados_caba\build_pdf_from_markdown_master.py |

### 10.b — Pasaron a SAFE_TO_DELETE_AFTER_APPROVAL desde REVIEW (60)

Eran REVIEW solo porque el validador viejo los exigía. Sin referencia funcional tras la actualización.

- `afirmaciones_mercados_v2_1.csv`
- `afirmaciones_mercados_v2_3.csv`
- `campos_objetivo_mercados.csv`
- `contradicciones_y_brechas_v2_1.csv`
- `contradicciones_y_brechas_v2_3.csv`
- `fuentes_documentales_mercados_v2.csv`
- `fuentes_documentales_mercados_v2_1.csv`
- `fuentes_documentales_mercados_v2_2.csv`
- `fuentes_documentales_mercados_v2_3.csv`
- `fuentes_mercados_candidatas.csv`
- `fuentes_mercados_urls_v0.csv`
- `fuentes_mercados_urls_v1.csv`
- `fuentes_mercados_urls_v1_2.csv`
- `fuentes_url_truncadas_requieren_verificacion_v2_3.csv`
- `horarios_documentados_mercados_vfinal_v2.csv`
- `indicadores_mercados_gastronomicos_v3.csv`
- `mercados_candidatos_iniciales.csv`
- `mercados_fuera_alcance_v0.csv`
- `mercados_gastronomicos_activos_v1.csv`
- `mercados_gastronomicos_activos_v1_2.csv`
- `mercados_gastronomicos_activos_v2.csv`
- `mercados_gastronomicos_activos_v2_2.csv`
- `mercados_gastronomicos_activos_v2_2.csv`
- `mercados_gastronomicos_activos_v2_4.csv`
- `mercados_gastronomicos_activos_v3.csv`
- `mercados_gastronomicos_candidatos_v0.csv`
- `mercados_gastronomicos_candidatos_v1.csv`
- `mercados_gastronomicos_candidatos_v1_2.csv`
- `mercados_gastronomicos_candidatos_v2.csv`
- `mercados_gastronomicos_candidatos_v2_2.csv`
- `mercados_gastronomicos_cerrados_o_no_activos_v1.csv`
- `mercados_gastronomicos_en_revision_v2_2.csv`
- `mercados_gastronomicos_en_revision_v2_2.csv`
- `mercados_gastronomicos_no_activos_v3.csv`
- `mercados_gastronomicos_no_contabilizados_v1_2.csv`
- `mercados_gastronomicos_no_contabilizados_v2.csv`
- `mercados_gastronomicos_no_contabilizados_v2_2.csv`
- `mercados_gastronomicos_pendientes_v1.csv`
- `mercados_gastronomicos_pendientes_v1_2.csv`
- `mercados_gastronomicos_posibles_omitidos_v2.csv`
- `mercados_gastronomicos_posibles_omitidos_v2_2.csv`
- `mercados_pendientes_revision_v0.csv`
- `oportunidades_politica_publica_mercados_v3.csv`
- `posibles_omitidos_documentales_v2_1.csv`
- `publicos_objetivo_mercados_v3.csv`
- `resumen_relevamiento_mercados_v0.csv`
- `resumen_relevamiento_mercados_v1.csv`
- `resumen_relevamiento_mercados_v1_2.csv`
- `resumen_relevamiento_mercados_v2.csv`
- `resumen_relevamiento_mercados_v2_2.csv`
- `resumen_relevamiento_mercados_v2_2.csv`
- `resumen_relevamiento_mercados_v2_4.csv`
- `resumen_relevamiento_mercados_v3.csv`
- `tabla_estado_y_no_contabilizados.csv`
- `tabla_por_barrio_comuna.csv`
- `tabla_por_gestion.csv`
- `tabla_por_tipo.csv`
- `tabla_universo.csv`
- `taxonomia_mercados.csv`
- `validacion_gourmand_food_hall_v2_4.csv`

### 10.c — KEEP_AS_ARCHIVE (53)

Valor histórico-documental; no requeridos por la cadena vigente. Recomendado moverlos luego a
`MercadosGastro/archive_review/` y `CasasDePastas/archive_review/`.

**casas_de_pastas/checkpoints_txt** (2): `DOMINGO_REVISION_FINAL_254.txt`, `SABADOALANOCHE_RECALL_GOOGLE_CHECKPOINT.txt`

**casas_de_pastas/docs_viejos** (2): `INFORME_CASAS_PASTAS.md`, `INFORME_CASAS_PASTAS_INTEGRADO.md`

**casas_de_pastas/informes_viejos** (7): `INFORME_CASAS_PASTAS.pdf`, `INFORME_CASAS_PASTAS_INTEGRADO.md`, `INFORME_CASAS_PASTAS_INTEGRADO.pdf`, `INFORME_CASAS_PASTAS_INTEGRADO_V2.md`, `INFORME_CASAS_PASTAS_INTEGRADO_V2.pdf`, `INFORME_CASAS_PASTAS_INTEGRADO_V3.md`, `INFORME_CASAS_PASTAS_INTEGRADO_V3.pdf`

**casas_de_pastas/packs_revision** (14): `DOMINGO_REVISION_FINAL_254.txt`, `INFORME_CASAS_PASTAS_INTEGRADO_V3.md`, `INFORME_CASAS_PASTAS_INTEGRADO_V3.pdf`, `MANIFIESTO_PACK_REVISION_EXTERNA_254.txt`, `PACK_REVISION_EXTERNA_254.zip`, `calidad_google_queries.csv`, `cobertura_cadenas_e_independientes.csv`, `densidad_integrado_por_barrio_v3_depurado.csv`, `densidad_integrado_por_comuna_v3_depurado.csv`, `integrado_por_barrio_v3_depurado.csv`, `integrado_por_comuna_v3_depurado.csv`, `integrado_por_fuente_v3_depurado.csv`, `mapa_puntos_sanitizado_v3_depurado.geojson`, `resumen_integrado_v3_depurado.csv`

**mercados_gastro/docs_versiones_viejas** (24): `ANEXO_FUENTES_Y_METODOLOGIA_MERCADOS_V4.md`, `ANEXO_HORARIOS_DOCUMENTADOS_MERCADOS_V2.md`, `ANEXO_TECNICO_MERCADOS_GASTRONOMICOS_CABA_V3.md`, `AUDITORIA_VISUAL_INFORME_FINAL_MERCADOS.md`, `AUDITORIA_VISUAL_INFORME_FINAL_MERCADOS_V4.md`, `AUDITORIA_VISUAL_INFORME_FINAL_MERCADOS_V4_1.md`, `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V3.md`, `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V4.md`, `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V5.md`, `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V5_1.md`, `INFORME_MERCADOS_GASTRONOMICOS_CABA_V1_2.md`, `INFORME_MERCADOS_GASTRONOMICOS_CABA_V2_2.md`, `OPORTUNIDAD_GESTION_MERCADOS_CABA_V4.md`, `README_REGENERAR_INFORME_FINAL.md`, `README_REGENERAR_INFORME_FINAL_V2.md`, `README_REGENERAR_INFORME_FINAL_V3.md`, `README_REGENERAR_INFORME_FINAL_V4.md`, `README_REGENERAR_INFORME_V4.md`, `README_REGENERAR_INFORME_V5.md`, `README_REGENERAR_INFORME_V5_1.md`, `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V3.md`, `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V5.md`, `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V5_1.md`, `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_V2_2.md`

**mercados_gastro/subcarpetas_intermedias** (4): `INFORME_MERCADOS_GASTRONOMICOS_CABA_V2_2.md`, `README_MERCADOS_DOCUMENTAL_V2_1.md`, `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_V2_2.md`, `resumen_narrativo_documental_v2_1.md`


---

## 11. Cierre de limpieza ejecutado (2026-06-29)

Aplicada la clasificación rev.2:

- **224 SAFE_TO_DELETE_AFTER_APPROVAL → ELIMINADOS** definitivamente de `_delete_candidates/`.
- **53 KEEP_AS_ARCHIVE → MOVIDOS** a `_archive_historico/<familia>/<subdir>/` (preservando el subdir de origen).
- **11 REVIEW_REQUIRED → PENDIENTES** en `_delete_candidates/mercados_gastro/csv_intermedios/`.
- **DO_NOT_DELETE: 0.**

### QA posterior al borrado/movimiento

| Prueba | Resultado |
|---|---|
| Mercados regenera (`build_pdf_final_con_horarios.py`) | ✅ OK |
| Casas de Pastas regenera (`build_pdf_integrado_v4.py`) | ✅ OK |
| DataGastro general (`validate_model.py --strict-real`) | ✅ OK=62, ERROR=0 |
| Validador Mercados (`validate_mercados_setup.py`) | ✅ EXIT 0, CADENA VIGENTE OK |
| PDF Mercados = 14 páginas | ✅ |
| p7 horarios documentales concretos | ✅ |
| p11 'Activar patios públicos como dinamizadores barriales.' | ✅ |
| p14 'Alcances del relevamiento y próximos pasos para consolidar la base candidata.' | ✅ |
| Footer 'DataGastro · Mercados gastronómicos de CABA · Informe final' | ✅ |
| PDF Mercados NO contiene 'V4_1' | ✅ |

### Rutas resultantes

- Archivo histórico: `_archive_historico/` (53 archivos: 28 mercados_gastro, 25 casas_de_pastas).
- Pendientes de revisión manual: `_delete_candidates/mercados_gastro/csv_intermedios/` (11 CSV).

### Confirmaciones

- ✅ Solo se borró dentro de `_delete_candidates/`. No se tocó V2, crudos, fuentes internas, `.env`, ni nada fuera de cuarentena.
- ✅ **Sin commit. Sin push. Sin `git add`.**

---

## 12. Resolución de los REVIEW_REQUIRED (2026-06-29)

Los **11 CSV** que quedaban en REVIEW_REQUIRED se resolvieron conservándolos como archivo histórico:

- **Movidos** de `_delete_candidates/mercados_gastro/csv_intermedios/` a
  `_archive_historico/mercados_gastro/csv_intermedios_referenciados/` (con `README.md` de metadata:
  ruta original + script que los referencia).
- **No se borraron.** No son necesarios para la cadena final de Mercados (probado), pero están
  referenciados por scripts secundarios / modos standalone de builders.
- **`_delete_candidates/` quedó vacío y se eliminó.** No hay archivos pendientes.
- **DO_NOT_DELETE: 0.**

### Estado final de la cuarentena

| Destino | Cantidad |
|---|---|
| Eliminados (SAFE) | 224 |
| Archivo histórico — KEEP | 53 |
| Archivo histórico — REVIEW referenciados | 11 |
| Pendientes en `_delete_candidates/` | 0 (carpeta eliminada) |
| **Total auditado** | **288** |

### QA posterior

| Prueba | Resultado |
|---|---|
| Mercados regenera | ✅ OK |
| Casas regenera | ✅ OK |
| DataGastro general (`validate_model --strict-real`) | ✅ OK=62, ERROR=0 |
| Validador Mercados (`validate_mercados_setup.py`) | ✅ EXIT 0 |

Sin commit. Sin push. Sin `git add`.
