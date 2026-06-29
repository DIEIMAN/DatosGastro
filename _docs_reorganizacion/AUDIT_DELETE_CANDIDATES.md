# AUDIT_DELETE_CANDIDATES — Auditoría de cuarentena (rev. 2 · validador actualizado)

**Fecha:** 2026-06-29 · **Archivos:** 288 · **Tamaño:** 45MB

> **CIERRE EJECUTADO (2026-06-29):** la clasificación rev.2 se aplicó.
>
> - **224 SAFE → ELIMINADOS** definitivamente.
> - **53 KEEP_AS_ARCHIVE → MOVIDOS** a `_archive_historico/<familia>/<subdir>/`.
> - **11 REVIEW_REQUIRED → ARCHIVADOS** en `_archive_historico/mercados_gastro/csv_intermedios_referenciados/`
>   (no se borraron; conservados como archivo histórico referenciado, con metadata en su `README.md`).
> - **DO_NOT_DELETE: 0.** La columna `disposition_2026_06_29` del `.csv` registra el destino de cada archivo.
> - **`_delete_candidates/` quedó vacío y se eliminó.** No hay nada pendiente.
> - Sin commit, sin push, sin `git add`. QA posterior OK (ver AUDIT_REORG_FINAL.md §11–§12).

Reclasificación tras actualizar `src/mercados_caba/validate_mercados_setup.py` para validar **solo
la cadena vigente**. Los archivos que antes eran REVIEW_REQUIRED únicamente porque el validador
viejo los exigía pasaron a SAFE o KEEP. Detalle fila-a-fila en `AUDIT_DELETE_CANDIDATES.csv`.

## Resumen por categoría

| Categoría | Antes (rev.1) | Ahora (rev.2) |
|---|---|---|
| SAFE_TO_DELETE_AFTER_APPROVAL | 164 | 224 |
| KEEP_AS_ARCHIVE | 42 | 53 |
| REVIEW_REQUIRED | 82 | 11 |
| DO_NOT_DELETE | 0 | 0 |
| **TOTAL** | **288** | **288** |

## REVIEW_REQUIRED (11)

### `mercados_gastro/csv_intermedios` (11)

> CSV con referencia en script vigente (no en la cadena del PDF final). Confirmar uso antes de borrar.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `candidatos_mercados_fuentes_internas_v2.csv` | 6KB | 2026-06-24 10:47 | src\mercados_caba\build_inventario_fuentes_internas_mercados… |
| `decisiones_que_permite_tomar_v4.csv` | 1KB | 2026-06-24 20:52 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `fuentes_internas_mercados_resumen_v2.csv` | 16KB | 2026-06-24 10:47 | src\mercados_caba\build_inventario_fuentes_internas_mercados… |
| `google_places_matches_v1_2.csv` | 2KB | 2026-06-24 10:51 | src\mercados_caba\google_places_mercados_enrichment.py |
| `google_places_mercados_resumen_v2.csv` | 712B | 2026-06-24 10:51 | src\mercados_caba\google_places_mercados_enrichment.py |
| `google_places_posibles_omitidos_v2.csv` | 5KB | 2026-06-24 10:51 | src\mercados_caba\google_places_mercados_enrichment.py |
| `mercados_gastronomicos_no_activos_v4.csv` | 2KB | 2026-06-24 20:52 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `oportunidades_gestion_mercados_v4.csv` | 3KB | 2026-06-26 10:49 | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `pilotos_recomendados_mercados_v4.csv` | 3KB | 2026-06-26 10:49 | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `publicos_objetivo_mercados_vfinal.csv` | 6KB | 2026-06-25 23:31 | src\mercados_caba\build_pdf_final_v4_1_from_v3.py; src\merca… |
| `referencias_documentales_visibles_v4.csv` | 2KB | 2026-06-24 20:53 | src\mercados_caba\build_pdf_from_markdown_master.py |

## KEEP_AS_ARCHIVE (53)

### `casas_de_pastas/checkpoints_txt` (2)

> Documento/informe/pack de versión superada con valor histórico-documental. No requerido por la cadena vigente (validador actualizado ya no lo exige).

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `DOMINGO_REVISION_FINAL_254.txt` | 7KB | 2026-06-21 10:31 | (ninguna funcional en cadena vigente) |
| `SABADOALANOCHE_RECALL_GOOGLE_CHECKPOINT.txt` | 10KB | 2026-06-20 23:55 | (ninguna funcional en cadena vigente) |

### `casas_de_pastas/docs_viejos` (2)

> Documento/informe/pack de versión superada con valor histórico-documental. No requerido por la cadena vigente (validador actualizado ya no lo exige).

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `INFORME_CASAS_PASTAS.md` | 8KB | 2026-06-19 17:01 | scripts\casas_pastas\build_casas_pastas.py |
| `INFORME_CASAS_PASTAS_INTEGRADO.md` | 4KB | 2026-06-20 14:09 | (ninguna funcional en cadena vigente) |

### `casas_de_pastas/informes_viejos` (7)

> Documento/informe/pack de versión superada con valor histórico-documental. No requerido por la cadena vigente (validador actualizado ya no lo exige).

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `INFORME_CASAS_PASTAS.pdf` | 137KB | 2026-06-20 11:24 | (ninguna funcional en cadena vigente) |
| `INFORME_CASAS_PASTAS_INTEGRADO.md` | 3KB | 2026-06-20 14:47 | (ninguna funcional en cadena vigente) |
| `INFORME_CASAS_PASTAS_INTEGRADO.pdf` | 152KB | 2026-06-20 14:47 | (ninguna funcional en cadena vigente) |
| `INFORME_CASAS_PASTAS_INTEGRADO_V2.md` | 4KB | 2026-06-20 16:24 | (ninguna funcional en cadena vigente) |
| `INFORME_CASAS_PASTAS_INTEGRADO_V2.pdf` | 239KB | 2026-06-20 16:24 | (ninguna funcional en cadena vigente) |
| `INFORME_CASAS_PASTAS_INTEGRADO_V3.md` | 6KB | 2026-06-21 18:11 | (ninguna funcional en cadena vigente) |
| `INFORME_CASAS_PASTAS_INTEGRADO_V3.pdf` | 816KB | 2026-06-21 18:11 | (ninguna funcional en cadena vigente) |

### `casas_de_pastas/packs_revision` (14)

> Documento/informe/pack de versión superada con valor histórico-documental. No requerido por la cadena vigente (validador actualizado ya no lo exige).

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `DOMINGO_REVISION_FINAL_254.txt` | 7KB | 2026-06-21 12:45 | (ninguna funcional en cadena vigente) |
| `INFORME_CASAS_PASTAS_INTEGRADO_V3.md` | 6KB | 2026-06-21 18:14 | (ninguna funcional en cadena vigente) |
| `INFORME_CASAS_PASTAS_INTEGRADO_V3.pdf` | 816KB | 2026-06-21 18:14 | (ninguna funcional en cadena vigente) |
| `MANIFIESTO_PACK_REVISION_EXTERNA_254.txt` | 2KB | 2026-06-21 18:13 | (ninguna funcional en cadena vigente) |
| `PACK_REVISION_EXTERNA_254.zip` | 796KB | 2026-06-21 18:14 | (ninguna funcional en cadena vigente) |
| `calidad_google_queries.csv` | 877B | 2026-06-20 14:08 | scripts\casas_pastas\google_places_integrar.py; scripts\casa… |
| `cobertura_cadenas_e_independientes.csv` | 397B | 2026-06-20 14:47 | scripts\casas_pastas\google_places_fix_cadenas.py; scripts\c… |
| `densidad_integrado_por_barrio_v3_depurado.csv` | 1KB | 2026-06-20 23:52 | scripts\casas_pastas\aplicar_revision_diego.py |
| `densidad_integrado_por_comuna_v3_depurado.csv` | 352B | 2026-06-20 23:52 | scripts\casas_pastas\aplicar_revision_diego.py |
| `integrado_por_barrio_v3_depurado.csv` | 1KB | 2026-06-20 23:52 | scripts\casas_pastas\aplicar_revision_diego.py |
| `integrado_por_comuna_v3_depurado.csv` | 352B | 2026-06-20 23:52 | scripts\casas_pastas\aplicar_revision_diego.py |
| `integrado_por_fuente_v3_depurado.csv` | 170B | 2026-06-21 12:43 | scripts\casas_pastas\aplicar_revision_diego.py |
| `mapa_puntos_sanitizado_v3_depurado.geojson` | 81KB | 2026-06-20 23:52 | scripts\casas_pastas\aplicar_revision_diego.py |
| `resumen_integrado_v3_depurado.csv` | 665B | 2026-06-20 23:52 | scripts\casas_pastas\aplicar_revision_diego.py; scripts\casa… |

### `mercados_gastro/docs_versiones_viejas` (24)

> Documento/informe/pack de versión superada con valor histórico-documental. No requerido por la cadena vigente (validador actualizado ya no lo exige).

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `ANEXO_FUENTES_Y_METODOLOGIA_MERCADOS_V4.md` | 6KB | 2026-06-26 10:49 | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `ANEXO_HORARIOS_DOCUMENTADOS_MERCADOS_V2.md` | 5KB | 2026-06-26 15:03 | (ninguna funcional en cadena vigente) |
| `ANEXO_TECNICO_MERCADOS_GASTRONOMICOS_CABA_V3.md` | 4KB | 2026-06-24 16:56 | (ninguna funcional en cadena vigente) |
| `AUDITORIA_VISUAL_INFORME_FINAL_MERCADOS.md` | 7KB | 2026-06-25 15:15 | (ninguna funcional en cadena vigente) |
| `AUDITORIA_VISUAL_INFORME_FINAL_MERCADOS_V4.md` | 8KB | 2026-06-26 11:17 | (ninguna funcional en cadena vigente) |
| `AUDITORIA_VISUAL_INFORME_FINAL_MERCADOS_V4_1.md` | 6KB | 2026-06-26 11:51 | (ninguna funcional en cadena vigente) |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V3.md` | 9KB | 2026-06-24 16:55 | (ninguna funcional en cadena vigente) |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V4.md` | 9KB | 2026-06-24 21:33 | (ninguna funcional en cadena vigente) |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V5.md` | 4KB | 2026-06-24 22:16 | (ninguna funcional en cadena vigente) |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V5_1.md` | 3KB | 2026-06-24 22:38 | (ninguna funcional en cadena vigente) |
| `INFORME_MERCADOS_GASTRONOMICOS_CABA_V1_2.md` | 15KB | 2026-06-24 10:07 | (ninguna funcional en cadena vigente) |
| `INFORME_MERCADOS_GASTRONOMICOS_CABA_V2_2.md` | 10KB | 2026-06-24 15:40 | (ninguna funcional en cadena vigente) |
| `OPORTUNIDAD_GESTION_MERCADOS_CABA_V4.md` | 9KB | 2026-06-26 10:49 | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `README_REGENERAR_INFORME_FINAL.md` | 1012B | 2026-06-25 15:14 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `README_REGENERAR_INFORME_FINAL_V2.md` | 1KB | 2026-06-25 15:14 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `README_REGENERAR_INFORME_FINAL_V3.md` | 1KB | 2026-06-25 23:31 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `README_REGENERAR_INFORME_FINAL_V4.md` | 1KB | 2026-06-26 11:07 | (ninguna funcional en cadena vigente) |
| `README_REGENERAR_INFORME_V4.md` | 2KB | 2026-06-24 21:33 | (ninguna funcional en cadena vigente) |
| `README_REGENERAR_INFORME_V5.md` | 468B | 2026-06-24 22:16 | (ninguna funcional en cadena vigente) |
| `README_REGENERAR_INFORME_V5_1.md` | 442B | 2026-06-24 22:38 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V3.md` | 2KB | 2026-06-24 16:55 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V5.md` | 616B | 2026-06-24 22:16 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V5_1.md` | 620B | 2026-06-24 22:38 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_V2_2.md` | 4KB | 2026-06-24 15:33 | (ninguna funcional en cadena vigente) |

### `mercados_gastro/subcarpetas_intermedias` (4)

> Documento narrativo/resumen de versión intermedia (V2.x) sin referencia funcional. Valor histórico-documental; conservar como archivo.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `INFORME_MERCADOS_GASTRONOMICOS_CABA_V2_2.md` | 9KB | 2026-06-24 11:46 | (ninguna funcional en cadena vigente) |
| `README_MERCADOS_DOCUMENTAL_V2_1.md` | 1KB | 2026-06-24 11:41 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_V2_2.md` | 4KB | 2026-06-24 15:33 | (ninguna funcional en cadena vigente) |
| `resumen_narrativo_documental_v2_1.md` | 4KB | 2026-06-24 11:41 | (ninguna funcional en cadena vigente) |

## SAFE_TO_DELETE_AFTER_APPROVAL (224)

### `casas_de_pastas/generadores_pdf_viejos` (4)

> Generador/validador de versión vieja, fuera de la cadena vigente. Reemplazado; las menciones en builders son strings de instrucciones, no imports.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `build_pdf_casas_pastas.py` | 14KB | 2026-06-20 11:23 | (ninguna funcional en cadena vigente) |
| `build_pdf_integrado.py` | 24KB | 2026-06-20 14:47 | (ninguna funcional en cadena vigente) |
| `build_pdf_integrado_v2.py` | 35KB | 2026-06-20 14:59 | (ninguna funcional en cadena vigente) |
| `build_pdf_integrado_v3.py` | 47KB | 2026-06-21 18:11 | (ninguna funcional en cadena vigente) |

### `mercados_gastro/csv_intermedios` (50)

> CSV intermedio de relevamiento v0-v3 sin referencia funcional en la cadena vigente ni en el validador actualizado.

_50 archivos — ver CSV para el detalle._

### `mercados_gastro/generadores_legacy` (7)

> Generador/validador de versión vieja, fuera de la cadena vigente. Reemplazado; las menciones en builders son strings de instrucciones, no imports.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `build_informe_final_v4.py` | 16KB | 2026-06-24 21:33 | (ninguna funcional en cadena vigente) |
| `build_informe_final_v5.py` | 25KB | 2026-06-24 22:15 | (ninguna funcional en cadena vigente) |
| `build_informe_final_v5_1.py` | 27KB | 2026-06-24 22:38 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `build_pdf_final_con_horarios_v2.py` | 16KB | 2026-06-26 15:03 | (ninguna funcional en cadena vigente) |
| `build_pdf_final_v4_from_v3.py` | 18KB | 2026-06-26 11:07 | (ninguna funcional en cadena vigente) |
| `build_visuals_v3.py` | 6KB | 2026-06-24 16:54 | (ninguna funcional en cadena vigente) |
| `build_visuals_v4.py` | 13KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |

### `mercados_gastro/packs_zip` (19)

> Salida regenerable (gráfico/mapa/pack/pdf/html) de versión vieja. No usada por la cadena vigente; el validador actualizado no la exige.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `PACK_COMPARTIBLE_MERCADOS_GASTRONOMICOS_CABA_V2_2.zip` | 8KB | 2026-06-24 15:35 | (ninguna funcional en cadena vigente) |
| `PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL.zip` | 732KB | 2026-06-25 15:14 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL_V2.zip` | 700KB | 2026-06-25 15:14 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL_V3.zip` | 3MB | 2026-06-25 23:31 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL_V4.zip` | 3MB | 2026-06-26 11:07 | (ninguna funcional en cadena vigente) |
| `PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_FINAL_V4_1.zip` | 3MB | 2026-06-26 11:49 | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_V3.zip` | 304KB | 2026-06-24 16:58 | (ninguna funcional en cadena vigente) |
| `PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_V4.zip` | 567KB | 2026-06-24 21:36 | (ninguna funcional en cadena vigente) |
| `PACK_ENTREGABLE_MERCADOS_GASTRONOMICOS_CABA_V5_1.zip` | 762KB | 2026-06-24 22:38 | (ninguna funcional en cadena vigente) |
| `PACK_INFORME_MERCADOS_GASTRONOMICOS_CABA_V1_2.zip` | 23KB | 2026-06-24 10:09 | (ninguna funcional en cadena vigente) |
| `PACK_MERCADOS_DOCUMENTAL_PERPLEXITY_V2_1.zip` | 11KB | 2026-06-24 11:10 | (ninguna funcional en cadena vigente) |
| `PACK_MERCADOS_DOCUMENTAL_URLS_VISIBLES_V2_3.zip` | 8KB | 2026-06-24 15:41 | (ninguna funcional en cadena vigente) |
| `PACK_MERCADOS_GASTRONOMICOS_CABA_V0.zip` | 52KB | 2026-06-23 17:57 | (ninguna funcional en cadena vigente) |
| `PACK_MERCADOS_GASTRONOMICOS_CABA_V1.zip` | 79KB | 2026-06-23 18:28 | (ninguna funcional en cadena vigente) |
| `PACK_MERCADOS_GASTRONOMICOS_CABA_V1_2.zip` | 96KB | 2026-06-23 18:39 | (ninguna funcional en cadena vigente) |
| `PACK_MERCADOS_GASTRONOMICOS_CABA_V2_2_CONSERVADOR.zip` | 33KB | 2026-06-24 11:48 | (ninguna funcional en cadena vigente) |
| `PACK_MERCADOS_GASTRONOMICOS_CABA_V2_ENRIQUECIDO.zip` | 22KB | 2026-06-24 10:56 | (ninguna funcional en cadena vigente) |
| `PACK_MercadosGastroCABA.zip` | 3MB | 2026-06-26 12:31 | src\mercados_caba\build_pdf_final_entrega.py |
| `PACK_MercadosGastroCABA_con_horarios_v2.zip` | 2MB | 2026-06-26 15:03 | (ninguna funcional en cadena vigente) |

### `mercados_gastro/pdfs_informes` (11)

> Salida regenerable (gráfico/mapa/pack/pdf/html) de versión vieja. No usada por la cadena vigente; el validador actualizado no la exige.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL.pdf` | 353KB | 2026-06-25 15:14 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL_V2.pdf` | 306KB | 2026-06-25 15:14 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL_V3.pdf` | 3MB | 2026-06-25 23:31 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL_V4.pdf` | 3MB | 2026-06-26 11:07 | (ninguna funcional en cadena vigente) |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_FINAL_V4_1.pdf` | 3MB | 2026-06-26 11:49 | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V3.pdf` | 209KB | 2026-06-24 16:56 | (ninguna funcional en cadena vigente) |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V4.pdf` | 309KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V5.pdf` | 362KB | 2026-06-24 22:16 | (ninguna funcional en cadena vigente) |
| `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_V5_1.pdf` | 367KB | 2026-06-24 22:38 | (ninguna funcional en cadena vigente) |
| `MercadosGastroCABA.pdf` | 3MB | 2026-06-26 12:31 | src\mercados_caba\build_pdf_final_entrega.py |
| `MercadosGastroCABA_con_horarios_v2.pdf` | 3MB | 2026-06-26 15:03 | (ninguna funcional en cadena vigente) |

### `mercados_gastro/pdfs_resumenes` (11)

> Salida regenerable (gráfico/mapa/pack/pdf/html) de versión vieja. No usada por la cadena vigente; el validador actualizado no la exige.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL.pdf` | 48KB | 2026-06-25 15:14 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL_V2.pdf` | 50KB | 2026-06-25 15:14 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL_V3.pdf` | 50KB | 2026-06-25 23:31 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL_V4.pdf` | 50KB | 2026-06-26 11:07 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_FINAL_V4_1.pdf` | 44KB | 2026-06-26 11:49 | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V3.pdf` | 4KB | 2026-06-24 16:56 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V4.pdf` | 4KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V5.pdf` | 41KB | 2026-06-24 22:16 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V5_1.pdf` | 42KB | 2026-06-24 22:38 | (ninguna funcional en cadena vigente) |
| `ResumenEjecutivo_MercadosGastroCABA.pdf` | 44KB | 2026-06-26 12:31 | src\mercados_caba\build_pdf_final_entrega.py |
| `ResumenEjecutivo_MercadosGastroCABA_con_horarios_v2.pdf` | 50KB | 2026-06-26 15:03 | (ninguna funcional en cadena vigente) |

### `mercados_gastro/qa_png` (86)

> Salida regenerable (gráfico/mapa/pack/pdf/html) de versión vieja. No usada por la cadena vigente; el validador actualizado no la exige.

_86 archivos — ver CSV para el detalle._

### `mercados_gastro/subcarpetas_intermedias` (14)

> Salida regenerable (gráfico/mapa/pack/pdf/html) de versión vieja. No usada por la cadena vigente; el validador actualizado no la exige.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `INFORME_MERCADOS_GASTRONOMICOS_CABA_V2_2.pdf` | 13KB | 2026-06-24 16:27 | (ninguna funcional en cadena vigente) |
| `RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_V2_2.pdf` | 6KB | 2026-06-24 16:27 | (ninguna funcional en cadena vigente) |
| `afirmaciones_mercados_v2_1.csv` | 5KB | 2026-06-24 11:41 | (ninguna funcional en cadena vigente) |
| `contradicciones_y_brechas_v2_1.csv` | 2KB | 2026-06-24 11:41 | (ninguna funcional en cadena vigente) |
| `fuentes_documentales_mercados_v2_1.csv` | 12KB | 2026-06-24 11:41 | (ninguna funcional en cadena vigente) |
| `mercados_gastronomicos_activos_v2_2.csv` | 2KB | 2026-06-24 11:43 | (ninguna funcional en cadena vigente) |
| `mercados_gastronomicos_en_revision_v2_2.csv` | 1KB | 2026-06-24 11:43 | (ninguna funcional en cadena vigente) |
| `posibles_omitidos_documentales_v2_1.csv` | 2KB | 2026-06-24 11:41 | (ninguna funcional en cadena vigente) |
| `resumen_relevamiento_mercados_v2_2.csv` | 2KB | 2026-06-24 11:44 | (ninguna funcional en cadena vigente) |
| `tabla_estado_y_no_contabilizados.csv` | 332B | 2026-06-24 10:08 | (ninguna funcional en cadena vigente) |
| `tabla_por_barrio_comuna.csv` | 557B | 2026-06-24 10:08 | (ninguna funcional en cadena vigente) |
| `tabla_por_gestion.csv` | 204B | 2026-06-24 10:08 | (ninguna funcional en cadena vigente) |
| `tabla_por_tipo.csv` | 479B | 2026-06-24 10:08 | (ninguna funcional en cadena vigente) |
| `tabla_universo.csv` | 574B | 2026-06-24 10:08 | (ninguna funcional en cadena vigente) |

### `mercados_gastro/validadores_legacy` (9)

> Generador/validador de versión vieja, fuera de la cadena vigente. Reemplazado; las menciones en builders son strings de instrucciones, no imports.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `validate_mercados_final.py` | 14KB | 2026-06-24 23:21 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `validate_mercados_final_con_horarios_v2.py` | 10KB | 2026-06-26 14:23 | (ninguna funcional en cadena vigente) |
| `validate_mercados_final_entrega.py` | 7KB | 2026-06-26 12:31 | (ninguna funcional en cadena vigente) |
| `validate_mercados_final_v2.py` | 6KB | 2026-06-25 15:13 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `validate_mercados_final_v3.py` | 8KB | 2026-06-25 23:29 | src\mercados_caba\build_pdf_from_markdown_master.py |
| `validate_mercados_final_v4.py` | 9KB | 2026-06-26 11:14 | (ninguna funcional en cadena vigente) |
| `validate_mercados_final_v4_1.py` | 9KB | 2026-06-26 11:43 | src\mercados_caba\build_pdf_final_v4_1_from_v3.py |
| `validate_mercados_v5.py` | 9KB | 2026-06-24 22:16 | (ninguna funcional en cadena vigente) |
| `validate_mercados_v5_1.py` | 9KB | 2026-06-24 22:39 | (ninguna funcional en cadena vigente) |

### `mercados_gastro/visuales_png` (13)

> Salida regenerable (gráfico/mapa/pack/pdf/html) de versión vieja. No usada por la cadena vigente; el validador actualizado no la exige.

| Archivo | Tam | mtime | Refs en código vigente |
|---|---|---|---|
| `grafico_comuna_barrio_v3.png` | 17KB | 2026-06-24 16:54 | (ninguna funcional en cadena vigente) |
| `grafico_gestion_v3.png` | 16KB | 2026-06-24 16:54 | (ninguna funcional en cadena vigente) |
| `grafico_gestion_v4.png` | 12KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |
| `grafico_horarios_v3.png` | 25KB | 2026-06-24 16:54 | (ninguna funcional en cadena vigente) |
| `grafico_horarios_v4.png` | 17KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |
| `grafico_kpi_cards_v4.png` | 44KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |
| `grafico_publicos_objetivo_v4.png` | 19KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |
| `grafico_respaldo_fuentes_v4.png` | 37KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |
| `grafico_tipo_mercado_v3.png` | 28KB | 2026-06-24 16:54 | (ninguna funcional en cadena vigente) |
| `grafico_tipo_primario_v4.png` | 25KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |
| `mapa_itinerantes_mercados_gastronomicos_v4.png` | 41KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |
| `mapa_mercados_gastronomicos_v3.png` | 76KB | 2026-06-24 16:54 | (ninguna funcional en cadena vigente) |
| `mapa_mercados_gastronomicos_v4.png` | 137KB | 2026-06-24 21:35 | (ninguna funcional en cadena vigente) |

## DO_NOT_DELETE (0)

_(ninguno — confirmado por la prueba fuerte de dependencia)_

